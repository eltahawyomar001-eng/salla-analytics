"""
Dynamic Schema Registry for Multi-Platform E-commerce Data Mapping

This module provides flexible, configuration-driven field definitions that can
adapt to different e-commerce platforms (Salla, Shopify, WooCommerce, etc.)
without requiring code changes.

Author: Salla Analytics Team
Created: October 2025
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import pandas as pd
from fuzzywuzzy import fuzz


class SchemaRegistry:
    """
    Dynamic schema management with multi-platform support.
    
    Replaces hardcoded CANONICAL_FIELDS with flexible JSON-based schema
    that can be extended without code changes.
    
    Features:
    - Multi-platform support (Salla, Shopify, WooCommerce, custom)
    - Auto-detection of platform from columns
    - Custom field registration
    - Intelligent field type detection
    - Synonym-based matching
    - Pattern-based detection
    """
    
    def __init__(self, schema_path: Optional[str] = None):
        """
        Initialize schema registry.
        
        Args:
            schema_path: Path to schema_registry.json. If None, uses default location.
        """
        if schema_path is None:
            # Default to app/schemas/schema_registry.json
            current_dir = Path(__file__).parent.parent
            schema_path = current_dir / "schemas" / "schema_registry.json"
        
        self.schema_path = Path(schema_path)
        self.schemas = self._load_schemas()
        self.custom_fields: Dict[str, Dict] = {}
        
    def _load_schemas(self) -> Dict:
        """Load schema definitions from JSON file."""
        try:
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Schema registry not found at {self.schema_path}. "
                "Please ensure schema_registry.json exists."
            )
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Invalid JSON in schema registry: {e}"
            )
    
    def get_platform_schema(self, platform: str = "salla") -> Dict:
        """
        Get complete schema for specific platform.
        
        Args:
            platform: Platform name (salla, shopify, woocommerce, custom)
            
        Returns:
            Dictionary containing platform configuration and field definitions
            
        Example:
            >>> registry = SchemaRegistry()
            >>> salla_schema = registry.get_platform_schema("salla")
            >>> print(salla_schema["core_fields"]["order_id"])
        """
        platform_lower = platform.lower()
        
        if platform_lower not in self.schemas.get("platforms", {}):
            # Fall back to Salla if platform not found
            print(f"Warning: Platform '{platform}' not found. Using Salla schema.")
            platform_lower = "salla"
        
        return self.schemas["platforms"][platform_lower]
    
    def get_all_platforms(self) -> List[str]:
        """Get list of all supported platforms."""
        return list(self.schemas.get("platforms", {}).keys())
    
    def detect_platform(self, columns: List[str]) -> str:
        """
        Auto-detect platform from column names.
        
        Uses fuzzy matching against known synonyms to determine
        which platform the data likely comes from.
        
        Args:
            columns: List of column names from uploaded file
            
        Returns:
            Platform name (salla, shopify, woocommerce, or custom)
            
        Example:
            >>> registry = SchemaRegistry()
            >>> columns = ["رقم الطلب", "تاريخ الطلب", "اسم العميل"]
            >>> platform = registry.detect_platform(columns)
            >>> print(platform)  # "salla"
        """
        if not columns:
            return "salla"  # Default
        
        scores = {}
        platforms = self.schemas.get("platforms", {})
        
        for platform_name, platform_config in platforms.items():
            score = 0
            total_fields = 0
            core_fields = platform_config.get("core_fields", {})
            
            # Check each core field's synonyms against columns
            for field_name, field_config in core_fields.items():
                if not field_config.get("required", False):
                    continue  # Only check required fields for platform detection
                
                total_fields += 1
                synonyms = field_config.get("synonyms", [])
                
                # Check if any synonym matches any column
                for synonym in synonyms:
                    for column in columns:
                        # Fuzzy match
                        similarity = fuzz.ratio(
                            synonym.lower(),
                            column.lower()
                        )
                        if similarity >= 80:  # 80% match threshold
                            score += 1
                            break
            
            # Calculate percentage of required fields matched
            if total_fields > 0:
                scores[platform_name] = score / total_fields
        
        if not scores:
            return "salla"  # Default
        
        # Get platform with highest score
        best_platform = max(scores.items(), key=lambda x: x[1])
        
        # Need at least 30% match to be confident
        if best_platform[1] >= 0.3:
            return best_platform[0]
        else:
            return "custom"  # Unknown platform
    
    def get_required_fields(self, platform: str = "salla") -> List[str]:
        """
        Get list of required field names for platform.
        
        Args:
            platform: Platform name
            
        Returns:
            List of required field names
            
        Example:
            >>> registry = SchemaRegistry()
            >>> required = registry.get_required_fields("salla")
            >>> print(required)  # ["order_id", "order_date", "customer_id", "order_total"]
        """
        schema = self.get_platform_schema(platform)
        core_fields = schema.get("core_fields", {})
        
        required = []
        for field_name, field_config in core_fields.items():
            if field_config.get("required", False):
                required.append(field_name)
        
        return required
    
    def get_optional_fields(self, platform: str = "salla") -> List[str]:
        """Get list of optional field names for platform."""
        schema = self.get_platform_schema(platform)
        core_fields = schema.get("core_fields", {})
        
        optional = []
        for field_name, field_config in core_fields.items():
            if not field_config.get("required", False):
                optional.append(field_name)
        
        return optional
    
    def get_all_fields(self, platform: str = "salla") -> List[str]:
        """Get all field names (required + optional) for platform."""
        schema = self.get_platform_schema(platform)
        return list(schema.get("core_fields", {}).keys())
    
    def get_field_config(self, field_name: str, platform: str = "salla") -> Optional[Dict]:
        """
        Get configuration for specific field.
        
        Args:
            field_name: Name of the field
            platform: Platform name
            
        Returns:
            Field configuration dict or None if not found
        """
        schema = self.get_platform_schema(platform)
        return schema.get("core_fields", {}).get(field_name)
    
    def add_custom_field(
        self, 
        field_name: str, 
        field_type: str = "string",
        required: bool = False,
        synonyms: Optional[List[str]] = None,
        description: str = "",
        category: str = "custom"
    ) -> bool:
        """
        Dynamically add a custom field to the registry.
        
        Args:
            field_name: Internal name for the field
            field_type: Data type (string, float, datetime, boolean)
            required: Whether field is required
            synonyms: List of alternative names
            description: Human-readable description
            category: Category (marketing, logistics, custom, etc.)
            
        Returns:
            True if added successfully
            
        Example:
            >>> registry = SchemaRegistry()
            >>> registry.add_custom_field(
            ...     "gift_message",
            ...     field_type="string",
            ...     synonyms=["Gift Message", "رسالة الهدية"],
            ...     description="Customer gift message"
            ... )
        """
        # Validate field type
        valid_types = ["string", "float", "datetime", "boolean"]
        if field_type not in valid_types:
            print(f"Warning: Invalid field type '{field_type}'. Using 'string'.")
            field_type = "string"
        
        # Create field config
        self.custom_fields[field_name] = {
            "required": required,
            "type": field_type,
            "synonyms": synonyms or [field_name],
            "description": description,
            "category": category,
            "custom": True,
            "created_at": datetime.now().isoformat()
        }
        
        return True
    
    def get_custom_fields(self) -> Dict[str, Dict]:
        """Get all registered custom fields."""
        return self.custom_fields
    
    def suggest_field_type(
        self, 
        column_name: str, 
        sample_data: pd.Series
    ) -> Tuple[str, float]:
        """
        Intelligently detect field type from sample data.
        
        Analyzes column name and sample values to suggest appropriate type.
        
        Args:
            column_name: Name of the column
            sample_data: Pandas series with sample values
            
        Returns:
            Tuple of (suggested_type, confidence_score)
            
        Example:
            >>> registry = SchemaRegistry()
            >>> sample = pd.Series(["2024-01-01", "2024-01-02", "2024-01-03"])
            >>> field_type, confidence = registry.suggest_field_type("order_date", sample)
            >>> print(field_type)  # "datetime"
        """
        # Remove nulls
        clean_data = sample_data.dropna()
        
        if len(clean_data) == 0:
            return "string", 0.5  # Default to string with low confidence
        
        # Check column name patterns
        name_lower = column_name.lower()
        
        # DateTime patterns
        date_patterns = [
            r'date', r'time', r'created', r'updated', r'تاريخ', r'وقت'
        ]
        if any(re.search(pattern, name_lower) for pattern in date_patterns):
            # Try parsing as date
            try:
                pd.to_datetime(clean_data.head(5))
                return "datetime", 0.9
            except:
                pass
        
        # Numeric patterns
        numeric_patterns = [
            r'total', r'amount', r'price', r'cost', r'quantity', 
            r'qty', r'count', r'إجمالي', r'مبلغ', r'كمية'
        ]
        if any(re.search(pattern, name_lower) for pattern in numeric_patterns):
            # Check if values are numeric
            try:
                pd.to_numeric(clean_data.head(5))
                return "float", 0.85
            except:
                pass
        
        # Boolean patterns
        boolean_patterns = [r'is_', r'has_', r'enabled', r'active']
        if any(re.search(pattern, name_lower) for pattern in boolean_patterns):
            unique_vals = set(str(v).lower() for v in clean_data.unique())
            boolean_vals = {'true', 'false', 'yes', 'no', '1', '0', 't', 'f'}
            if unique_vals.issubset(boolean_vals):
                return "boolean", 0.9
        
        # Analyze actual values
        try:
            # Try numeric conversion
            numeric_vals = pd.to_numeric(clean_data, errors='coerce')
            numeric_ratio = numeric_vals.notna().sum() / len(clean_data)
            
            if numeric_ratio > 0.8:
                return "float", numeric_ratio
        except:
            pass
        
        # Try datetime conversion
        try:
            date_vals = pd.to_datetime(clean_data, errors='coerce')
            date_ratio = date_vals.notna().sum() / len(clean_data)
            
            if date_ratio > 0.8:
                return "datetime", date_ratio
        except:
            pass
        
        # Default to string
        return "string", 0.6
    
    def get_field_synonyms(self, field_name: str, platform: str = "salla") -> List[str]:
        """
        Get all synonyms for a field.
        
        Args:
            field_name: Field name
            platform: Platform name
            
        Returns:
            List of synonym strings
        """
        field_config = self.get_field_config(field_name, platform)
        
        if field_config:
            return field_config.get("synonyms", [])
        
        # Check custom fields
        if field_name in self.custom_fields:
            return self.custom_fields[field_name].get("synonyms", [])
        
        return []
    
    def get_field_patterns(self, field_name: str, platform: str = "salla") -> List[str]:
        """Get auto-detection patterns for a field."""
        field_config = self.get_field_config(field_name, platform)
        
        if field_config:
            return field_config.get("auto_detect_patterns", [])
        
        return []
    
    def validate_field_value(
        self, 
        field_name: str, 
        value: Any, 
        platform: str = "salla"
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a value against field's validation rules.
        
        Args:
            field_name: Field to validate
            value: Value to check
            platform: Platform name
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        field_config = self.get_field_config(field_name, platform)
        
        if not field_config:
            return True, None  # Unknown field, allow it
        
        # Check required
        if field_config.get("required", False) and pd.isna(value):
            return False, f"{field_name} is required"
        
        # Check type
        field_type = field_config.get("type", "string")
        validators = field_config.get("validators", [])
        
        # TODO: Implement specific validators
        # For now, just check basic type compatibility
        
        return True, None
    
    def to_canonical_fields_dict(self, platform: str = "salla") -> Dict[str, Dict]:
        """
        Convert schema to CANONICAL_FIELDS format for backward compatibility.
        
        Args:
            platform: Platform to generate schema for
            
        Returns:
            Dictionary in CANONICAL_FIELDS format
            
        Example:
            >>> registry = SchemaRegistry()
            >>> canonical = registry.to_canonical_fields_dict("salla")
            >>> print(canonical["order_id"])  # {"required": True, "type": "string"}
        """
        schema = self.get_platform_schema(platform)
        core_fields = schema.get("core_fields", {})
        
        canonical = {}
        for field_name, field_config in core_fields.items():
            canonical[field_name] = {
                "required": field_config.get("required", False),
                "type": field_config.get("type", "string")
            }
        
        # Add custom fields
        for field_name, field_config in self.custom_fields.items():
            canonical[field_name] = {
                "required": field_config.get("required", False),
                "type": field_config.get("type", "string")
            }
        
        return canonical
    
    def get_schema_version(self) -> str:
        """Get schema registry version."""
        return self.schemas.get("version", "1.0.0")
    
    def __repr__(self) -> str:
        """String representation."""
        platforms = self.get_all_platforms()
        custom_count = len(self.custom_fields)
        
        return (
            f"SchemaRegistry(version={self.get_schema_version()}, "
            f"platforms={platforms}, "
            f"custom_fields={custom_count})"
        )


# Example usage and testing
if __name__ == "__main__":
    # Initialize registry
    registry = SchemaRegistry()
    
    print("=" * 60)
    print("Schema Registry Test")
    print("=" * 60)
    
    # Test 1: Platform detection
    print("\n1. Platform Detection:")
    salla_columns = ["رقم الطلب", "تاريخ الطلب", "اسم العميل"]
    shopify_columns = ["Name", "Email", "Created at", "Total"]
    
    print(f"   Salla columns: {registry.detect_platform(salla_columns)}")
    print(f"   Shopify columns: {registry.detect_platform(shopify_columns)}")
    
    # Test 2: Required fields
    print("\n2. Required Fields:")
    for platform in registry.get_all_platforms():
        required = registry.get_required_fields(platform)
        print(f"   {platform.title()}: {required}")
    
    # Test 3: Custom field
    print("\n3. Adding Custom Field:")
    registry.add_custom_field(
        "gift_message",
        field_type="string",
        synonyms=["Gift Message", "رسالة الهدية"],
        description="Customer gift message"
    )
    print(f"   Custom fields: {list(registry.get_custom_fields().keys())}")
    
    # Test 4: Field type detection
    print("\n4. Field Type Detection:")
    sample_dates = pd.Series(["2024-01-01", "2024-01-02", "2024-01-03"])
    sample_numbers = pd.Series([100.5, 200.0, 350.75])
    
    date_type, date_conf = registry.suggest_field_type("order_date", sample_dates)
    num_type, num_conf = registry.suggest_field_type("total_amount", sample_numbers)
    
    print(f"   'order_date' samples → {date_type} ({date_conf:.0%} confidence)")
    print(f"   'total_amount' samples → {num_type} ({num_conf:.0%} confidence)")
    
    # Test 5: Backward compatibility
    print("\n5. Backward Compatibility (CANONICAL_FIELDS format):")
    canonical = registry.to_canonical_fields_dict("salla")
    print(f"   Generated {len(canonical)} fields")
    print(f"   Sample: {list(canonical.items())[:3]}")
    
    print("\n" + "=" * 60)
    print(f"✅ Schema Registry initialized successfully!")
    print(f"   Version: {registry.get_schema_version()}")
    print(f"   Platforms: {', '.join(registry.get_all_platforms())}")
    print("=" * 60)
