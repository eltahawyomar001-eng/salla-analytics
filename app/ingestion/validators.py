"""Data validation and quality checks for Salla exports."""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Set
from datetime import datetime
import re

from ..config import CANONICAL_FIELDS, QUALITY_THRESHOLDS

logger = logging.getLogger(__name__)

class DataValidator:
    """Validates and cleans Salla export data."""
    
    def __init__(self):
        self.validation_rules = self._load_validation_rules()
        
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load validation rules for each field type."""
        return {
            'order_id': {
                'type': 'string',
                'required': True,
                'unique': True,
                'min_length': 1
            },
            'order_date': {
                'type': 'datetime',
                'required': True,
                'min_date': '2000-01-01',
                'max_date': None  # Current date
            },
            'customer_id': {
                'type': 'string',
                'required': True,
                'min_length': 1
            },
            'order_total': {
                'type': 'numeric',
                'required': True,
                'min_value': 0
            },
            'currency': {
                'type': 'string',
                'valid_values': ['SAR', 'USD', 'EUR', 'AED', 'KWD', 'BHD', 'QAR', 'OMR']
            },
            'quantity': {
                'type': 'numeric',
                'min_value': 0
            }
        }
    
    def validate_dataframe(
        self, 
        df: pd.DataFrame, 
        mappings: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Comprehensive validation of mapped DataFrame.
        
        Args:
            df: DataFrame to validate
            mappings: Column mappings (canonical -> source)
            
        Returns:
            Validation results dictionary
        """
        results = {
            'is_valid': True,
            'total_rows': len(df),
            'errors': [],
            'warnings': [],
            'data_quality': {},
            'cleaning_applied': [],
            'duplicates_found': 0,
            'invalid_rows': 0,
            'currency_info': {},
            'date_range': {}
        }
        
        # Create mapped DataFrame
        mapped_df = self._create_mapped_dataframe(df, mappings)
        
        # Run validation checks
        self._validate_required_fields(mapped_df, mappings, results)
        self._validate_data_types(mapped_df, results)
        self._check_data_quality(mapped_df, results)
        self._detect_duplicates(mapped_df, results)
        self._validate_business_rules(mapped_df, results)
        self._analyze_currencies(mapped_df, results)
        self._analyze_date_ranges(mapped_df, results)
        
        # Set overall validity
        results['is_valid'] = len(results['errors']) == 0
        
        return results
    
    def _create_mapped_dataframe(
        self, 
        df: pd.DataFrame, 
        mappings: Dict[str, str]
    ) -> pd.DataFrame:
        """Create DataFrame with canonical column names."""
        mapped_df = pd.DataFrame()
        
        for canonical_field, source_column in mappings.items():
            if source_column in df.columns:
                mapped_df[canonical_field] = df[source_column].copy()
        
        return mapped_df
    
    def _validate_required_fields(
        self, 
        df: pd.DataFrame, 
        mappings: Dict[str, str], 
        results: Dict[str, Any]
    ) -> None:
        """Validate that required fields are present and not empty."""
        required_fields = [
            field for field, config in CANONICAL_FIELDS.items()
            if config.get('required', False)
        ]
        
        for field in required_fields:
            if field not in mappings:
                results['errors'].append(f"Required field '{field}' is not mapped")
            elif field in df.columns:
                null_count = df[field].isnull().sum()
                null_percentage = (null_count / len(df)) * 100
                
                if null_percentage > 20:
                    results['warnings'].append(
                        f"Required field '{field}' has {null_percentage:.1f}% missing values"
                    )
                
                if null_percentage > 50:
                    results['errors'].append(
                        f"Required field '{field}' has too many missing values ({null_percentage:.1f}%)"
                    )
    
    def _validate_data_types(self, df: pd.DataFrame, results: Dict[str, Any]) -> None:
        """Validate and attempt to convert data types."""
        type_conversions = {
            'order_total': 'numeric',
            'quantity': 'numeric',
            'item_total': 'numeric',
            'discounts': 'numeric',
            'shipping': 'numeric',
            'taxes': 'numeric',
            'refund_amount': 'numeric',
            'order_date': 'datetime'
        }
        
        # Text fields that should NEVER be converted to numeric
        text_only_fields = {
            'country', 'city', 'state', 'province', 'region',
            'customer_name', 'customer_email', 'customer_phone',
            'product_name', 'product_sku', 'product_category',
            'order_status', 'payment_method', 'shipping_method'
        }
        
        for field, target_type in type_conversions.items():
            if field not in df.columns:
                continue
            
            # Extra safety: Skip if column name suggests it's a text field
            if any(text_field in field.lower() for text_field in text_only_fields):
                logger.warning(f"Skipping type conversion for '{field}' - appears to be text column")
                continue
                
            try:
                if target_type == 'numeric':
                    # Try to convert to numeric
                    original_series = df[field].copy()
                    converted = pd.to_numeric(df[field], errors='coerce')
                    
                    # Check conversion success rate
                    non_null_original = original_series.dropna()
                    non_null_converted = converted.dropna()
                    
                    if len(non_null_original) > 0:
                        success_rate = len(non_null_converted) / len(non_null_original)
                        
                        if success_rate < 0.5:
                            # Less than 50% conversion - critical issue
                            results['errors'].append(
                                f"Field '{field}' cannot be converted to numeric ({success_rate:.1%} success rate)"
                            )
                        elif success_rate < 0.8:
                            # Between 50-80% - warning but continue
                            results['warnings'].append(
                                f"Field '{field}' has low numeric conversion rate ({success_rate:.1%})"
                            )
                            df[field] = converted
                            results['cleaning_applied'].append(f"Converted '{field}' to numeric (with some loss)")
                        else:
                            # Above 80% - good conversion
                            df[field] = converted
                            results['cleaning_applied'].append(f"Converted '{field}' to numeric")
                    else:
                        # No non-null values to convert
                        results['warnings'].append(f"Field '{field}' has no non-null values")
                
                elif target_type == 'datetime':
                    # Try multiple date formats
                    converted = None
                    original_non_null = df[field].dropna()
                    
                    # Try common date formats
                    date_formats = [
                        None,  # pandas auto-detection
                        '%Y-%m-%d',  # ISO format
                        '%d/%m/%Y',  # European
                        '%m/%d/%Y',  # US
                        '%Y/%m/%d',  # Alternative ISO
                        '%d.%m.%Y',  # German
                        '%d-%m-%Y',  # Alternative European
                    ]
                    
                    best_converted = None
                    best_success_rate = 0
                    
                    for date_format in date_formats:
                        try:
                            if date_format is None:
                                temp_converted = pd.to_datetime(df[field], errors='coerce')
                            else:
                                temp_converted = pd.to_datetime(df[field], format=date_format, errors='coerce')
                            
                            success_rate = temp_converted.notna().sum() / len(original_non_null) if len(original_non_null) > 0 else 0
                            
                            if success_rate > best_success_rate:
                                best_success_rate = success_rate
                                best_converted = temp_converted
                                
                            # If we get >95% success, stop trying
                            if success_rate > 0.95:
                                break
                        except Exception:
                            continue
                    
                    if best_converted is not None:
                        if best_success_rate < 0.5:
                            results['errors'].append(
                                f"Field '{field}' cannot be converted to datetime ({best_success_rate:.1%} success rate)"
                            )
                        elif best_success_rate < 0.8:
                            results['warnings'].append(
                                f"Field '{field}' has low datetime conversion rate ({best_success_rate:.1%})"
                            )
                            df[field] = best_converted
                            results['cleaning_applied'].append(f"Converted '{field}' to datetime (with some loss)")
                        else:
                            df[field] = best_converted
                            results['cleaning_applied'].append(f"Converted '{field}' to datetime")
                    else:
                        results['errors'].append(f"Field '{field}' could not be parsed as datetime with any known format")
            
            except Exception as e:
                logger.error(f"Error converting field '{field}' to {target_type}: {e}", exc_info=True)
                results['errors'].append(f"Error converting '{field}' to {target_type}: {str(e)}")
    
    def _check_data_quality(self, df: pd.DataFrame, results: Dict[str, Any]) -> None:
        """Check overall data quality metrics."""
        quality_metrics = {}
        
        for column in df.columns:
            series = df[column]
            
            metrics = {
                'total_rows': len(series),
                'null_count': series.isnull().sum(),
                'null_percentage': (series.isnull().sum() / len(series)) * 100,
                'unique_count': series.nunique(),
                'unique_percentage': (series.nunique() / len(series)) * 100 if len(series) > 0 else 0,
                'data_type': str(series.dtype)
            }
            
            # Check for sparse fields
            if metrics['null_percentage'] > 95:
                results['warnings'].append(
                    f"Field '{column}' is sparse ({metrics['null_percentage']:.1f}% missing)"
                )
            
            quality_metrics[column] = metrics
        
        results['data_quality'] = quality_metrics
    
    def _detect_duplicates(self, df: pd.DataFrame, results: Dict[str, Any]) -> None:
        """Detect and analyze duplicate records."""
        duplicate_checks = []
        
        # Check for order-level duplicates
        if 'order_id' in df.columns:
            order_duplicates = df['order_id'].duplicated().sum()
            if order_duplicates > 0:
                duplicate_checks.append({
                    'type': 'order_id',
                    'count': order_duplicates,
                    'percentage': (order_duplicates / len(df)) * 100
                })
        
        # Check for line item duplicates
        line_item_cols = ['order_id', 'product_id', 'line_item_id']
        available_cols = [col for col in line_item_cols if col in df.columns]
        
        if len(available_cols) >= 2:
            line_duplicates = df.duplicated(subset=available_cols).sum()
            if line_duplicates > 0:
                duplicate_checks.append({
                    'type': 'line_item',
                    'count': line_duplicates,
                    'percentage': (line_duplicates / len(df)) * 100,
                    'columns_used': available_cols
                })
        
        # Store results
        total_duplicates = sum(check['count'] for check in duplicate_checks)
        results['duplicates_found'] = total_duplicates
        results['duplicate_details'] = duplicate_checks
        
        if total_duplicates > 0:
            results['warnings'].append(f"Found {total_duplicates} duplicate records")
    
    def _validate_business_rules(self, df: pd.DataFrame, results: Dict[str, Any]) -> None:
        """Validate business logic rules."""
        invalid_count = 0
        
        # Rule 1: Order total should be >= 0
        if 'order_total' in df.columns:
            negative_totals = (df['order_total'] < 0).sum()
            if negative_totals > 0:
                results['warnings'].append(f"Found {negative_totals} orders with negative totals")
                invalid_count += negative_totals
        
        # Rule 2: Quantities should be > 0
        if 'quantity' in df.columns:
            zero_quantities = (df['quantity'] <= 0).sum()
            if zero_quantities > 0:
                results['warnings'].append(f"Found {zero_quantities} line items with zero/negative quantity")
                invalid_count += zero_quantities
        
        # Rule 3: Dates should be reasonable
        if 'order_date' in df.columns:
            current_date = pd.Timestamp.now()
            future_dates = (df['order_date'] > current_date).sum()
            old_dates = (df['order_date'] < pd.Timestamp('2000-01-01')).sum()
            
            if future_dates > 0:
                results['warnings'].append(f"Found {future_dates} orders with future dates")
                invalid_count += future_dates
            
            if old_dates > 0:
                results['warnings'].append(f"Found {old_dates} orders with very old dates (before 2000)")
                invalid_count += old_dates
        
        # Rule 4: Customer and order IDs should not be empty
        for id_field in ['customer_id', 'order_id']:
            if id_field in df.columns:
                empty_ids = df[id_field].astype(str).str.strip().eq('').sum()
                if empty_ids > 0:
                    results['errors'].append(f"Found {empty_ids} records with empty {id_field}")
                    invalid_count += empty_ids
        
        results['invalid_rows'] = invalid_count
    
    def _analyze_currencies(self, df: pd.DataFrame, results: Dict[str, Any]) -> None:
        """Analyze currency distribution and detect issues."""
        currency_info = {
            'currencies_found': [],
            'currency_distribution': {},
            'missing_currency_count': 0,
            'mixed_currencies': False,
            'default_currency': None
        }
        
        if 'currency' in df.columns:
            # Get currency distribution
            currency_counts = df['currency'].value_counts(dropna=False)
            currency_info['currency_distribution'] = currency_counts.to_dict()
            currency_info['currencies_found'] = [
                curr for curr in currency_counts.index 
                if pd.notna(curr)
            ]
            currency_info['missing_currency_count'] = df['currency'].isnull().sum()
            
            # Check for mixed currencies
            valid_currencies = [curr for curr in currency_info['currencies_found'] if curr != '']
            if len(valid_currencies) > 1:
                currency_info['mixed_currencies'] = True
                results['warnings'].append(
                    f"Multiple currencies detected: {', '.join(valid_currencies)}"
                )
            
            # Determine default currency
            if valid_currencies:
                currency_info['default_currency'] = currency_counts.index[0]
            else:
                currency_info['default_currency'] = None  # No currency specified
                results['warnings'].append("No currency information found - using generic currency format")
        else:
            currency_info['default_currency'] = None
            results['warnings'].append("No currency column found - using generic currency format")
        
        results['currency_info'] = currency_info
    
    def _analyze_date_ranges(self, df: pd.DataFrame, results: Dict[str, Any]) -> None:
        """Analyze date ranges in the data."""
        date_info = {}
        
        if 'order_date' in df.columns:
            valid_dates = df['order_date'].dropna()
            
            if len(valid_dates) > 0:
                date_info = {
                    'min_date': valid_dates.min(),
                    'max_date': valid_dates.max(),
                    'date_span_days': (valid_dates.max() - valid_dates.min()).days,
                    'total_orders': len(valid_dates),
                    'orders_per_day': len(valid_dates) / max(1, (valid_dates.max() - valid_dates.min()).days)
                }
                
                # Check for reasonable date ranges
                if date_info['date_span_days'] < 1:
                    results['warnings'].append("All orders are from the same day")
                elif date_info['date_span_days'] > 365 * 5:  # More than 5 years
                    results['warnings'].append(
                        f"Data spans {date_info['date_span_days']} days ({date_info['date_span_days']/365:.1f} years)"
                    )
        
        results['date_range'] = date_info
    
    def clean_dataframe(
        self, 
        df: pd.DataFrame, 
        mappings: Dict[str, str],
        remove_duplicates: bool = True,
        remove_invalid: bool = True,
        already_mapped: bool = False
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Clean the DataFrame based on validation results.
        
        Args:
            df: Original DataFrame
            mappings: Column mappings
            remove_duplicates: Whether to remove duplicate records
            remove_invalid: Whether to remove invalid records
            already_mapped: If True, df already has canonical column names
            
        Returns:
            Tuple of (cleaned_DataFrame, cleaning_summary)
        """
        cleaning_summary = {
            'original_rows': len(df),
            'removed_rows': 0,
            'cleaning_steps': [],
            'final_rows': 0
        }
        
        # Create working copy
        df_clean = df.copy()
        
        # Determine column names to use
        if already_mapped:
            # Columns already have canonical names
            col_map = {k: k for k in mappings.keys()}
        else:
            # Use the mapping to get source column names
            col_map = mappings
            # Create mapped version for validation
            mapped_df = self._create_mapped_dataframe(df_clean, mappings)
        
        # Remove duplicates if requested
        if remove_duplicates:
            if 'order_id' in col_map:
                before_count = len(df_clean)
                order_id_col = col_map['order_id']
                if order_id_col in df_clean.columns:
                    df_clean = df_clean.drop_duplicates(subset=[order_id_col])
                    removed = before_count - len(df_clean)
                    
                    if removed > 0:
                        cleaning_summary['removed_rows'] += removed
                        cleaning_summary['cleaning_steps'].append(f"Removed {removed} duplicate orders")
        
        # Remove invalid records if requested
        if remove_invalid:
            # Remove records with negative order totals
            if 'order_total' in col_map:
                total_col = col_map['order_total']
                if total_col in df_clean.columns:
                    before_count = len(df_clean)
                    df_clean = df_clean[pd.to_numeric(df_clean[total_col], errors='coerce') >= 0]
                    removed = before_count - len(df_clean)
                    
                    if removed > 0:
                        cleaning_summary['removed_rows'] += removed
                        cleaning_summary['cleaning_steps'].append(f"Removed {removed} records with negative totals")
            
            # Remove records with empty required IDs
            for id_field in ['order_id', 'customer_id']:
                if id_field in col_map:
                    id_col = col_map[id_field]
                    if id_col in df_clean.columns:
                        before_count = len(df_clean)
                        df_clean = df_clean[
                            df_clean[id_col].astype(str).str.strip() != ''
                        ]
                        removed = before_count - len(df_clean)
                        
                        if removed > 0:
                            cleaning_summary['removed_rows'] += removed
                            cleaning_summary['cleaning_steps'].append(
                                f"Removed {removed} records with empty {id_field}"
                            )
        
        cleaning_summary['final_rows'] = len(df_clean)
        
        return df_clean, cleaning_summary

def validate_salla_data(
    df: pd.DataFrame, 
    mappings: Dict[str, str]
) -> Dict[str, Any]:
    """
    Convenience function to validate Salla export data.
    
    Args:
        df: DataFrame to validate
        mappings: Column mappings (canonical -> source)
        
    Returns:
        Validation results
    """
    validator = DataValidator()
    return validator.validate_dataframe(df, mappings)

def clean_salla_data(
    df: pd.DataFrame, 
    mappings: Dict[str, str]
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Convenience function to clean Salla export data.
    
    Args:
        df: DataFrame to clean
        mappings: Column mappings
        
    Returns:
        Tuple of (cleaned_DataFrame, cleaning_summary)
    """
    validator = DataValidator()
    return validator.clean_dataframe(df, mappings)