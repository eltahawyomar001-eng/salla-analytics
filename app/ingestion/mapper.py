"""Column mapping and schema detection for Salla exports."""

import json
import logging
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import re

try:
    from fuzzywuzzy import fuzz
    FUZZYWUZZY_AVAILABLE = True
except ImportError:
    FUZZYWUZZY_AVAILABLE = False

from ..config import CANONICAL_FIELDS, SCHEMAS_DIR, QUALITY_THRESHOLDS

logger = logging.getLogger(__name__)

class ColumnMapper:
    """Handles automatic column detection and mapping."""
    
    def __init__(self):
        self.synonyms = self._load_synonyms()
        self.canonical_schema = self._load_canonical_schema()
        self.mapping_cache: Dict[str, Dict[str, str]] = {}
        
    def _load_synonyms(self) -> Dict[str, Any]:
        """Load header synonyms from YAML file."""
        synonyms_file = SCHEMAS_DIR / "header_synonyms.yaml"
        try:
            with open(synonyms_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Could not load synonyms file: {e}")
            return {"synonyms": {}}
    
    def _load_canonical_schema(self) -> Dict[str, Any]:
        """Load canonical schema from YAML file."""
        schema_file = SCHEMAS_DIR / "canonical_schema.yaml"
        try:
            with open(schema_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Could not load schema file: {e}")
            return {"canonical_schema": {}}
    
    def normalize_header(self, header: str) -> str:
        """Normalize header for better matching."""
        if not isinstance(header, str):
            header = str(header)
            
        # Convert to lowercase and strip whitespace
        normalized = header.lower().strip()
        
        # Remove common prefixes/suffixes
        normalized = re.sub(r'^(col_|column_|field_)', '', normalized)
        normalized = re.sub(r'(_col|_column|_field)$', '', normalized)
        
        # Replace common separators with underscore
        normalized = re.sub(r'[-\s\.]+', '_', normalized)
        
        # Remove special characters except underscore
        normalized = re.sub(r'[^\w\u0600-\u06FF_]', '', normalized)
        
        return normalized
    
    def calculate_match_score(
        self, 
        source_header: str, 
        target_synonyms: List[str]
    ) -> float:
        """Calculate match score between source header and target synonyms."""
        source_norm = self.normalize_header(source_header)
        
        best_score = 0.0
        
        for synonym in target_synonyms:
            synonym_norm = self.normalize_header(synonym)
            
            # Exact match
            if source_norm == synonym_norm:
                return 1.0
            
            # Fuzzy match
            if FUZZYWUZZY_AVAILABLE:
                fuzzy_score = fuzz.ratio(source_norm, synonym_norm) / 100.0  # type: ignore
                # Token sort ratio for better handling of word order
                token_score = fuzz.token_sort_ratio(source_norm, synonym_norm) / 100.0  # type: ignore
                # Take the best of fuzzy and token scores
                score = max(fuzzy_score, token_score)
            else:
                # Fallback to simple string matching
                if synonym_norm in source_norm or source_norm in synonym_norm:
                    score = 0.8
                else:
                    score = 0.0
            
            # Partial match bonus
            if synonym_norm in source_norm or source_norm in synonym_norm:
                score += 0.1
            
            if score > best_score:
                best_score = score
        
        return min(best_score, 1.0)
    
    def auto_detect_columns(
        self, 
        df: pd.DataFrame, 
        confidence_threshold: Optional[float] = None
    ) -> Tuple[Dict[str, str], Dict[str, float]]:
        """
        Automatically detect column mappings.
        
        Args:
            df: DataFrame to analyze
            confidence_threshold: Minimum confidence for auto-detection
            
        Returns:
            Tuple of (mappings_dict, confidence_scores)
        """
        if confidence_threshold is None:
            confidence_threshold = QUALITY_THRESHOLDS['mapping_confidence_threshold']
        
        mappings = {}
        confidence_scores = {}
        
        source_columns = list(df.columns)
        
        # Get synonyms for each canonical field
        synonyms = self.synonyms.get('synonyms', {})
        
        for canonical_field in CANONICAL_FIELDS.keys():
            best_match = None
            best_score = 0.0
            
            # Get all synonyms for this field
            field_synonyms = []
            if canonical_field in synonyms:
                field_synonyms.extend(synonyms[canonical_field].get('english', []))
                field_synonyms.extend(synonyms[canonical_field].get('arabic', []))
            
            # Add the canonical field name itself
            field_synonyms.append(canonical_field)
            
            # Test each source column
            for source_col in source_columns:
                score = self.calculate_match_score(source_col, field_synonyms)
                
                if score > best_score:
                    best_score = score
                    best_match = source_col
            
            # Store if above threshold
            threshold = confidence_threshold or QUALITY_THRESHOLDS['mapping_confidence_threshold']
            if best_match and best_score >= threshold:
                mappings[canonical_field] = best_match
                confidence_scores[canonical_field] = best_score
            else:
                confidence_scores[canonical_field] = best_score
        
        # Ensure no duplicate mappings
        mappings = self._resolve_mapping_conflicts(mappings, confidence_scores)
        
        return mappings, confidence_scores
    
    def _resolve_mapping_conflicts(
        self, 
        mappings: Dict[str, str], 
        scores: Dict[str, float]
    ) -> Dict[str, str]:
        """Resolve conflicts where multiple canonical fields map to same source column."""
        source_to_canonical = {}
        conflicts = {}
        
        # Find conflicts
        for canonical, source in mappings.items():
            if source in source_to_canonical:
                # Conflict detected
                existing_canonical = source_to_canonical[source]
                
                if source not in conflicts:
                    conflicts[source] = [(existing_canonical, scores[existing_canonical])]
                
                conflicts[source].append((canonical, scores[canonical]))
            else:
                source_to_canonical[source] = canonical
        
        # Resolve conflicts by keeping highest scoring mapping
        resolved_mappings = mappings.copy()
        
        for source_col, candidates in conflicts.items():
            # Sort by score descending
            candidates.sort(key=lambda x: x[1], reverse=True)
            
            # Keep only the best one
            winner = candidates[0][0]
            
            # Remove others
            for canonical, _ in candidates[1:]:
                if canonical in resolved_mappings:
                    del resolved_mappings[canonical]
        
        return resolved_mappings
    
    def _detect_line_item_data(self, df: pd.DataFrame, mappings: Dict[str, str]) -> bool:
        """
        Detect if data is at line-item level (needs aggregation).
        
        Args:
            df: DataFrame to check
            mappings: Current column mappings
            
        Returns:
            True if data appears to be line-item level
        """
        # Indicator 1: Has order_item_id but no order_id
        has_order_item = 'order_item_id' in df.columns
        has_order_id = 'order_id' in mappings or 'order_id' in df.columns
        
        if has_order_item and not has_order_id:
            return True
        
        # Indicator 2: Has product/item columns
        item_cols = ['item_id', 'product_id', 'sku', 'item_size', 'item_color', 'item_price']
        has_item_cols = any(col in df.columns for col in item_cols)
        
        if has_item_cols and not has_order_id:
            return True
        
        # Indicator 3: Has line_item_id or quantity columns
        line_cols = ['line_item_id', 'quantity', 'item_quantity']
        has_line_cols = any(col in df.columns for col in line_cols)
        
        if has_line_cols and not has_order_id:
            return True
        
        return False
    
    def validate_mappings(
        self, 
        df: pd.DataFrame, 
        mappings: Dict[str, str]
    ) -> Dict[str, Any]:
        """Validate column mappings and check data quality."""
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'field_stats': {},
            'missing_required': [],
            'data_quality_score': 0.0
        }
        
        # Check if data appears to be line-item level (will be aggregated)
        is_line_item_data = self._detect_line_item_data(df, mappings)
        
        # Check required fields
        required_fields = [
            field for field, config in CANONICAL_FIELDS.items() 
            if config.get('required', False)
        ]
        
        for field in required_fields:
            # Special case: order_id not required for line-item data (will be created during aggregation)
            if field == 'order_id' and is_line_item_data:
                if field not in mappings:
                    validation_results['warnings'].append(
                        "order_id will be generated during aggregation (line-item data detected)"
                    )
                    continue
            
            # Special case: customer_id can be derived from phone or email
            if field == 'customer_id' and field not in mappings:
                if 'customer_phone' in mappings:
                    mappings['customer_id'] = mappings['customer_phone']
                    validation_results['warnings'].append(
                        "Using customer_phone as customer_id (no dedicated customer ID column found)"
                    )
                    continue
                elif 'customer_email' in mappings:
                    mappings['customer_id'] = mappings['customer_email']
                    validation_results['warnings'].append(
                        "Using customer_email as customer_id (no dedicated customer ID column found)"
                    )
                    continue
            
            if field not in mappings:
                validation_results['missing_required'].append(field)
                validation_results['errors'].append(f"Required field '{field}' not mapped")
        
        # Analyze mapped columns
        total_fields = len(mappings)
        quality_scores = []
        
        for canonical_field, source_column in mappings.items():
            if source_column in df.columns:
                series = df[source_column]
                
                # Calculate field statistics
                stats = self._analyze_field_quality(series, canonical_field)
                validation_results['field_stats'][canonical_field] = stats
                
                quality_scores.append(stats['quality_score'])
                
                # Add warnings for poor quality fields
                if stats['null_percentage'] > 95:
                    validation_results['warnings'].append(
                        f"Field '{canonical_field}' is mostly empty ({stats['null_percentage']:.1f}% null)"
                    )
                
                if stats['quality_score'] < 0.3:
                    validation_results['warnings'].append(
                        f"Field '{canonical_field}' has poor data quality"
                    )
            else:
                validation_results['errors'].append(
                    f"Mapped column '{source_column}' not found in data"
                )
        
        # Calculate overall quality score
        if quality_scores:
            validation_results['data_quality_score'] = sum(quality_scores) / len(quality_scores)
        
        # Set validity
        validation_results['is_valid'] = (
            len(validation_results['missing_required']) == 0 and
            len(validation_results['errors']) == 0
        )
        
        return validation_results
    
    def _analyze_field_quality(self, series: pd.Series, field_type: str) -> Dict[str, Any]:
        """Analyze the quality of a mapped field."""
        stats = {
            'total_rows': len(series),
            'null_count': series.isnull().sum(),
            'null_percentage': (series.isnull().sum() / len(series)) * 100,
            'unique_count': series.nunique(),
            'data_type': str(series.dtype),
            'quality_score': 0.0,
            'sample_values': []
        }
        
        # Get sample values
        non_null_values = series.dropna()
        if len(non_null_values) > 0:
            stats['sample_values'] = list(non_null_values.head(5).astype(str))
        
        # Calculate quality score based on field type and content
        quality_score = 1.0
        
        # Penalize high null percentage
        if stats['null_percentage'] > 50:
            quality_score *= 0.5
        elif stats['null_percentage'] > 20:
            quality_score *= 0.8
        
        # Field-specific quality checks
        expected_type = CANONICAL_FIELDS.get(field_type, {}).get('type', 'string')
        
        if expected_type == 'float' and series.dtype not in ['int64', 'float64']:
            # Try to convert sample to see if it's numeric
            try:
                pd.to_numeric(non_null_values.head(100), errors='raise')
            except:
                quality_score *= 0.7
        
        elif expected_type == 'datetime':
            # Check if looks like dates
            try:
                pd.to_datetime(non_null_values.head(100), errors='raise')
            except:
                quality_score *= 0.7
        
        # Bonus for reasonable unique counts
        if field_type in ['customer_id', 'order_id', 'product_id']:
            unique_ratio = stats['unique_count'] / max(stats['total_rows'] - stats['null_count'], 1)
            if unique_ratio < 0.8:  # Expect mostly unique values for IDs
                quality_score *= 0.8
        
        stats['quality_score'] = max(0.0, min(1.0, quality_score))
        
        return stats
    
    def save_mapping(
        self, 
        file_key: str, 
        mappings: Dict[str, str]
    ) -> None:
        """Save column mapping for future use."""
        cache_file = Path.cwd() / ".salla_mappings.json"
        
        try:
            # Load existing cache
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
            else:
                cache = {}
            
            # Update cache
            cache[file_key] = mappings
            
            # Save cache
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Saved mapping for {file_key}")
            
        except Exception as e:
            logger.warning(f"Could not save mapping cache: {e}")
    
    def load_mapping(self, file_key: str) -> Optional[Dict[str, str]]:
        """Load previously saved column mapping."""
        cache_file = Path.cwd() / ".salla_mappings.json"
        
        try:
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                    return cache.get(file_key)
        except Exception as e:
            logger.warning(f"Could not load mapping cache: {e}")
        
        return None
    
    def get_mapping_suggestions(
        self, 
        df: pd.DataFrame, 
        unmapped_fields: List[str]
    ) -> Dict[str, List[Tuple[str, float]]]:
        """Get mapping suggestions for unmapped fields."""
        suggestions = {}
        
        source_columns = list(df.columns)
        synonyms = self.synonyms.get('synonyms', {})
        
        for field in unmapped_fields:
            field_suggestions = []
            
            # Get synonyms for this field
            field_synonyms = []
            if field in synonyms:
                field_synonyms.extend(synonyms[field].get('english', []))
                field_synonyms.extend(synonyms[field].get('arabic', []))
            field_synonyms.append(field)
            
            # Score all source columns
            for source_col in source_columns:
                score = self.calculate_match_score(source_col, field_synonyms)
                if score > 0.3:  # Only include reasonable matches
                    field_suggestions.append((source_col, score))
            
            # Sort by score descending
            field_suggestions.sort(key=lambda x: x[1], reverse=True)
            
            # Keep top 3 suggestions
            suggestions[field] = field_suggestions[:3]
        
        return suggestions

def create_file_key(file_path: str, file_size: int) -> str:
    """Create a unique key for caching file mappings."""
    path_obj = Path(file_path)
    return f"{path_obj.stem}_{file_size}_{path_obj.suffix}"

def auto_map_columns(df: pd.DataFrame) -> Tuple[Dict[str, str], Dict[str, float]]:
    """
    Convenience function for automatic column mapping.
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        Tuple of (mappings, confidence_scores)
    """
    mapper = ColumnMapper()
    return mapper.auto_detect_columns(df)