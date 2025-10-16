"""Geographic analytics module for revenue and customer distribution.

This module provides flexible location-based analysis that works with various
e-commerce data formats (Salla, international platforms, etc.).
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
import logging

logger = logging.getLogger(__name__)


class GeoAnalyzer:
    """Analyzes geographic distribution of revenue and customers.
    
    Works flexibly with multiple data formats and location hierarchies.
    """
    
    def __init__(self, df: pd.DataFrame):
        """Initialize geo analyzer.
        
        Args:
            df: DataFrame with order data
        """
        self.df = df.copy()
        self.location_columns = self._detect_location_columns()
        self.has_location_data = any(v is not None for v in self.location_columns.values())
        
        logger.info(f"GeoAnalyzer initialized with {len(df)} rows")
        logger.info(f"Detected location columns: {self.location_columns}")
        logger.info(f"Has location data: {self.has_location_data}")
        
    def _detect_location_columns(self) -> Dict[str, Optional[str]]:
        """Detect location-related columns intelligently.
        
        Returns comprehensive mapping of location types to column names.
        Supports multiple languages and naming conventions.
        """
        columns: Dict[str, Optional[str]] = {
            'city': None,
            'state': None,
            'country': None,
            'region': None,
            'province': None,
            'county': None,
            'postal_code': None,
            'address': None
        }
        
        # Comprehensive patterns for each location type
        # Supports: English, Arabic, German, French, Spanish, and common variations
        patterns = {
            'city': [
                # English
                'city', 'cities', 'town', 'locality', 'user_city', 'customer_city',
                'billing_city', 'shipping_city', 'delivery_city',
                # Arabic
                'المدينة', 'مدينة',
                # Other languages
                'ville', 'ciudad', 'città', 'stadt', 'şehir'
            ],
            'state': [
                # English
                'state', 'states', 'user_state', 'customer_state', 
                'billing_state', 'shipping_state', 'province_state',
                # Arabic
                'الولاية', 'ولاية',
                # Other languages
                'état', 'estado', 'stato', 'bundesland'
            ],
            'country': [
                # English
                'country', 'countries', 'nation', 'user_country', 
                'customer_country', 'billing_country', 'shipping_country',
                'country_name', 'country_code', 'iso_country',
                # Arabic
                'الدولة', 'دولة', 'البلد', 'بلد',
                # Other languages
                'pays', 'país', 'paese', 'land', 'ülke'
            ],
            'region': [
                # English
                'region', 'regions', 'area', 'zone', 'district', 'territory',
                # Arabic
                'المنطقة', 'منطقة',
                # Other languages
                'région', 'región', 'regione', 'bölge'
            ],
            'province': [
                # English
                'province', 'provinces', 'governorate', 'prefecture',
                # Arabic
                'المحافظة', 'محافظة',
                # Other languages
                'provincia', 'prefectur'
            ],
            'county': [
                # English
                'county', 'counties', 'borough', 'shire', 'kreis',
                # Arabic
                'المقاطعة', 'مقاطعة',
                # Other languages
                'comté', 'condado', 'contea', 'ilçe'
            ],
            'postal_code': [
                # English
                'postal', 'zip', 'zipcode', 'zip_code', 'postal_code',
                'postcode', 'postalcode', 'postal code',
                # Arabic - be specific to avoid matching coupon codes
                'الرمز البريدي', 'رمز بريدي',
                # Other languages
                'code_postal', 'código_postal', 'plz', 'cap'
            ],
            'address': [
                # English
                'address', 'street', 'full_address', 'customer_address',
                'billing_address', 'shipping_address', 'delivery_address',
                # Arabic
                'عنوان', 'العنوان', 'عنوان العميل',
                # Other languages
                'adresse', 'dirección', 'indirizzo'
            ]
        }
        
        # Convert all column names to lowercase for matching
        df_columns_lower = {str(col).lower().strip(): str(col) for col in self.df.columns}
        
        # Match patterns to actual columns
        for field, field_patterns in patterns.items():
            for pattern in field_patterns:
                pattern_lower = pattern.lower().strip()
                
                # Try exact match first
                if pattern_lower in df_columns_lower:
                    columns[field] = df_columns_lower[pattern_lower]
                    logger.debug(f"Exact match: {field} = '{columns[field]}'")
                    break
                
                # Try partial match (pattern contained in column name)
                # Only if pattern is long enough to avoid false positives (min 4 chars)
                if len(pattern_lower) >= 4:
                    for col_lower, col_original in df_columns_lower.items():
                        if pattern_lower in col_lower:
                            # Additional validation: avoid matching coupon/code columns for postal
                            if field == 'postal_code':
                                # Skip if column contains 'coupon', 'كوبون', 'discount', 'خصم', 'promo'
                                if any(skip in col_lower for skip in ['coupon', 'كوبون', 'discount', 'خصم', 'promo', 'voucher']):
                                    continue
                            
                            columns[field] = col_original
                            logger.debug(f"Partial match: {field} = '{columns[field]}'")
                            break
                
                if columns[field]:
                    break
        
        # Post-processing validation: Remove invalid location columns
        columns_to_validate = ['postal_code', 'address']
        for field in columns_to_validate:
            col_name = columns.get(field)
            if col_name and col_name in self.df.columns:
                # Check if it looks like real location data
                unique_ratio = self.df[col_name].nunique() / len(self.df)
                
                # If almost every row has unique value (>80%), it's likely not a real location field
                # (could be customer names, IDs, full addresses, etc.)
                if unique_ratio > 0.8:
                    logger.warning(f"Removing {field} '{col_name}' - too many unique values ({unique_ratio:.1%})")
                    columns[field] = None
        
        return columns
    
    def get_revenue_by_location(
        self,
        location_type: str = 'city',
        min_orders: int = 1,
        top_n: Optional[int] = None
    ) -> pd.DataFrame:
        """Aggregate revenue by geographic location.
        
        Args:
            location_type: Type of location ('city', 'state', 'country', 'region', etc.)
            min_orders: Minimum number of orders to include location
            top_n: Return only top N locations by revenue (None = all)
            
        Returns:
            DataFrame with columns: location, revenue, orders, customers, 
                                   avg_order_value, revenue_per_customer, revenue_pct
        """
        location_col = self.location_columns.get(location_type)
        
        if location_col is None or location_col not in self.df.columns:
            logger.warning(f"Location type '{location_type}' not found in data")
            return pd.DataFrame()
        
        # Filter out null locations
        df_filtered = self.df[self.df[location_col].notna()].copy()
        
        if df_filtered.empty:
            logger.warning(f"No non-null data for location column '{location_col}'")
            return pd.DataFrame()
        
        # Detect revenue column (flexible)
        revenue_col = self._detect_revenue_column(df_filtered)
        if not revenue_col:
            logger.error("No revenue column found in data")
            return pd.DataFrame()
        
        # Detect customer ID column (flexible)
        customer_col = self._detect_customer_column(df_filtered)
        if not customer_col:
            logger.error("No customer column found in data")
            return pd.DataFrame()
        
        logger.info(f"Aggregating by {location_col}, revenue={revenue_col}, customer={customer_col}")
        
        # Aggregate by location
        agg_dict = {
            revenue_col: 'sum',
            customer_col: 'nunique'
        }
        
        geo_df = df_filtered.groupby(location_col, as_index=False).agg(agg_dict)
        
        # Count orders
        order_counts = df_filtered.groupby(location_col).size().reset_index(name='orders')
        geo_df = geo_df.merge(order_counts, on=location_col)
        
        # Rename columns to standard names
        geo_df = geo_df.rename(columns={
            location_col: 'location',
            revenue_col: 'revenue',
            customer_col: 'customers'
        })
        
        # Keep original location column name for reference
        geo_df['location_type'] = location_type
        geo_df['location_column'] = location_col
        
        # Filter by minimum orders
        geo_df = geo_df[geo_df['orders'] >= min_orders]
        
        if geo_df.empty:
            logger.warning(f"No locations with >= {min_orders} orders")
            return pd.DataFrame()
        
        # Calculate derived metrics
        geo_df['avg_order_value'] = geo_df['revenue'] / geo_df['orders']
        geo_df['revenue_per_customer'] = geo_df['revenue'] / geo_df['customers']
        
        # Calculate percentage of total revenue
        total_revenue = geo_df['revenue'].sum()
        geo_df['revenue_pct'] = (geo_df['revenue'] / total_revenue * 100).round(2)
        
        # Sort by revenue
        geo_df = geo_df.sort_values('revenue', ascending=False).reset_index(drop=True)
        
        # Apply top N filter if specified
        if top_n is not None and top_n > 0:
            geo_df = geo_df.head(top_n)
        
        logger.info(f"Aggregated {len(geo_df)} locations")
        
        return geo_df
    
    def _detect_revenue_column(self, df: pd.DataFrame) -> Optional[str]:
        """Detect the revenue/amount column flexibly."""
        candidates = [
            # English
            'sales', 'total', 'amount', 'revenue', 'value', 'price',
            'order_total', 'total_amount', 'total_sales', 'grand_total',
            'item_price', 'order_value', 'sale_amount',
            # Arabic
            'إجمالي الطلب', 'مجموع السلة', 'المجموع', 'السعر', 'القيمة',
            # Keep original case variations
            'Sales', 'Total', 'Amount', 'Revenue', 'Value', 'Price'
        ]
        
        # Try exact matches first
        for col in df.columns:
            if col in candidates:
                if pd.api.types.is_numeric_dtype(df[col]):
                    return col
        
        # Try case-insensitive partial matches
        for col in df.columns:
            col_lower = str(col).lower()
            for candidate in candidates:
                if candidate.lower() in col_lower:
                    if pd.api.types.is_numeric_dtype(df[col]):
                        return col
        
        return None
    
    def _detect_customer_column(self, df: pd.DataFrame) -> Optional[str]:
        """Detect the customer ID column flexibly."""
        candidates = [
            # English
            'customer_id', 'customer', 'user_id', 'user', 'client_id', 'client',
            'customer_number', 'cust_id', 'customerid',
            # Arabic
            'رقم الجوال', 'رقم العميل', 'العميل', 'اسم العميل',
            # Keep original case
            'Customer ID', 'User ID', 'Customer', 'User'
        ]
        
        # Try exact matches
        for col in df.columns:
            if col in candidates:
                return col
        
        # Try partial matches
        for col in df.columns:
            col_lower = str(col).lower()
            for candidate in candidates:
                if candidate.lower() in col_lower:
                    return col
        
        return None
    
    def get_location_summary(self) -> Dict[str, Any]:
        """Get summary of available location data.
        
        Returns:
            Dictionary with has_data flag and available location fields
        """
        if not self.has_location_data:
            return {
                'has_data': False,
                'message': 'No location data found in dataset'
            }
        
        summary = {
            'has_data': True,
            'available_fields': []
        }
        
        for field, col_name in self.location_columns.items():
            if col_name and col_name in self.df.columns:
                unique_count = self.df[col_name].nunique()
                non_null_count = self.df[col_name].notna().sum()
                coverage_pct = (non_null_count / len(self.df) * 100) if len(self.df) > 0 else 0
                
                if unique_count > 0:
                    summary['available_fields'].append({
                        'field': field,
                        'column': col_name,
                        'unique_values': int(unique_count),
                        'non_null_count': int(non_null_count),
                        'coverage_pct': round(coverage_pct, 1)
                    })
        
        return summary
    
    def get_top_locations(
        self,
        location_type: str = 'city',
        top_n: int = 10
    ) -> pd.DataFrame:
        """Get top N locations by revenue.
        
        Args:
            location_type: Type of location
            top_n: Number of top locations to return
            
        Returns:
            DataFrame with top locations
        """
        return self.get_revenue_by_location(location_type, min_orders=1, top_n=top_n)
    
    def get_geographic_insights(self, location_type: str = 'city') -> Dict[str, Any]:
        """Generate insights about geographic distribution.
        
        Args:
            location_type: Type of location to analyze
            
        Returns:
            Dictionary with insights (concentration, top location, etc.)
        """
        geo_df = self.get_revenue_by_location(location_type, min_orders=1)
        
        if geo_df.empty:
            return {}
        
        total_locations = len(geo_df)
        
        # Revenue concentration
        top_5_revenue = geo_df.head(5)['revenue'].sum()
        total_revenue = geo_df['revenue'].sum()
        concentration_pct = (top_5_revenue / total_revenue * 100) if total_revenue > 0 else 0
        
        # Top location
        top_location = geo_df.iloc[0]
        
        # Highest AOV location
        highest_aov_idx = geo_df['avg_order_value'].idxmax()
        highest_aov_location = geo_df.loc[highest_aov_idx]
        
        # Extract scalar values from Series
        def extract_value(val: Any) -> Any:
            """Extract scalar value from potential Series."""
            if hasattr(val, 'iloc'):
                return val.iloc[0]
            return val
        
        # Type-safe extraction with explicit conversion
        def to_float(val: Any) -> float:
            """Convert value to float safely."""
            extracted = extract_value(val)
            return float(extracted) if extracted is not None else 0.0
        
        def to_int(val: Any) -> int:
            """Convert value to int safely."""
            extracted = extract_value(val)
            return int(extracted) if extracted is not None else 0
        
        def to_str(val: Any) -> str:
            """Convert value to str safely."""
            extracted = extract_value(val)
            return str(extracted) if extracted is not None else ''
        
        insights = {
            'total_locations': total_locations,
            'concentration': {
                'top_5_pct': round(concentration_pct, 1),
                'description': 'High' if concentration_pct > 60 else 'Medium' if concentration_pct > 40 else 'Low'
            },
            'top_location': {
                'name': to_str(top_location['location']),
                'revenue': to_float(top_location['revenue']),
                'orders': to_int(top_location['orders']),
                'customers': to_int(top_location['customers']),
                'revenue_pct': to_float(top_location['revenue_pct'])
            },
            'highest_aov_location': {
                'name': to_str(highest_aov_location['location']),
                'aov': to_float(highest_aov_location['avg_order_value']),
                'orders': to_int(highest_aov_location['orders'])
            }
        }
        
        return insights
    
    def get_country_for_map(self) -> Optional[str]:
        """Detect the primary country in the dataset for map centering.
        
        Returns:
            ISO country code or country name if detected, None otherwise
        """
        country_col = self.location_columns.get('country')
        
        if not country_col or country_col not in self.df.columns:
            return None
        
        # Get most common country
        country_counts = self.df[country_col].value_counts()
        
        if country_counts.empty:
            return None
        
        primary_country = country_counts.index[0]
        
        # Map common country names to ISO codes for better map support
        country_map = {
            'Saudi Arabia': 'SAU',
            'السعودية': 'SAU',
            'المملكة العربية السعودية': 'SAU',
            'Germany': 'DEU',
            'Deutschland': 'DEU',
            'Australia': 'AUS',
            'New Zealand': 'NZL',
            'United States': 'USA',
            'United Kingdom': 'GBR',
            'France': 'FRA',
            'Spain': 'ESP',
            'Italy': 'ITA'
        }
        
        return country_map.get(str(primary_country), str(primary_country))
