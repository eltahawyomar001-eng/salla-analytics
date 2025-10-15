"""Data aggregation utilities for converting line-item data to order-level data."""

import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class DataAggregator:
    """Aggregates line-item level data to order-level for analysis."""
    
    def __init__(self):
        self.aggregation_strategy = None
        
    def detect_data_level(self, df: pd.DataFrame, mappings: Dict[str, str]) -> Dict[str, Any]:
        """
        Detect if data is at order-level or line-item level.
        
        Args:
            df: DataFrame to analyze
            mappings: Column mappings
            
        Returns:
            Detection results with strategy recommendation
        """
        results = {
            'data_level': 'unknown',
            'confidence': 0.0,
            'indicators': [],
            'requires_aggregation': False,
            'aggregation_strategy': None
        }
        
        # Check for line-item indicators
        line_item_indicators = []
        
        # Indicator 1: Has product/item columns
        product_cols = ['product_id', 'product_name', 'item_id', 'sku', 'item_size', 'item_color']
        has_product = any(col in df.columns for col in product_cols)
        if has_product:
            line_item_indicators.append('Has product/item columns')
        
        # Indicator 2: Has quantity or line_item_id
        line_item_cols = ['quantity', 'line_item_id', 'order_item_id', 'item_price']
        has_line_items = any(col in df.columns for col in line_item_cols)
        if has_line_items:
            line_item_indicators.append('Has line-item columns')
        
        # Indicator 3: Multiple rows per customer+date
        if 'customer_id' in df.columns and 'order_date' in df.columns:
            try:
                customer_date_groups = df.groupby(['customer_id', 'order_date']).size()
                avg_items_per_order = customer_date_groups.mean()
                
                if avg_items_per_order > 1.5:
                    line_item_indicators.append(f'Avg {avg_items_per_order:.1f} items per customer-date')
                    results['avg_items_per_order'] = avg_items_per_order
            except Exception as e:
                logger.warning(f"Could not analyze customer-date groups: {e}")
        
        # Indicator 4: Has order_item_id but no order_id
        has_order_item = 'order_item_id' in df.columns
        has_order_id = 'order_id' in df.columns
        
        if has_order_item and not has_order_id:
            line_item_indicators.append('Has order_item_id but no order_id')
        
        # Determine data level
        if len(line_item_indicators) >= 2:
            results['data_level'] = 'line_item'
            results['confidence'] = min(0.95, len(line_item_indicators) * 0.25)
            results['requires_aggregation'] = True
            results['aggregation_strategy'] = self._recommend_strategy(df, mappings)
        else:
            results['data_level'] = 'order'
            results['confidence'] = 0.8
            results['requires_aggregation'] = False
        
        results['indicators'] = line_item_indicators
        
        return results
    
    def _recommend_strategy(self, df: pd.DataFrame, mappings: Dict[str, str]) -> str:
        """Recommend aggregation strategy based on available columns."""
        
        # Strategy 1: Has order_id - group by order_id
        if 'order_id' in df.columns:
            return 'group_by_order_id'
        
        # Strategy 2: Has customer + date + can infer orders
        if 'customer_id' in df.columns and 'order_date' in df.columns:
            return 'group_by_customer_date'
        
        # Strategy 3: Sequential order_item_id (Germany data pattern)
        if 'order_item_id' in df.columns and 'customer_id' in df.columns and 'order_date' in df.columns:
            return 'group_by_customer_date_sequential'
        
        return 'unknown'
    
    def aggregate_to_orders(
        self, 
        df: pd.DataFrame, 
        mappings: Dict[str, str],
        strategy: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Aggregate line-item data to order-level data.
        
        Args:
            df: Line-item DataFrame
            mappings: Column mappings
            strategy: Aggregation strategy (auto-detect if None)
            
        Returns:
            Order-level DataFrame with canonical columns
        """
        if strategy is None:
            detection = self.detect_data_level(df, mappings)
            strategy = detection['aggregation_strategy']
        
        logger.info(f"Aggregating line-item data using strategy: {strategy}")
        
        if strategy == 'group_by_order_id':
            return self._aggregate_by_order_id(df)
        elif strategy == 'group_by_customer_date':
            return self._aggregate_by_customer_date(df)
        elif strategy == 'group_by_customer_date_sequential':
            return self._aggregate_by_customer_date_sequential(df)
        else:
            raise ValueError(f"Unknown aggregation strategy: {strategy}")
    
    def _aggregate_by_order_id(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate when order_id exists."""
        
        agg_functions = {
            'order_date': 'first',
            'customer_id': 'first',
        }
        
        # Add price aggregation
        price_cols = ['item_price', 'price', 'unit_price', 'order_total']
        for col in price_cols:
            if col in df.columns:
                agg_functions[col] = 'sum'
                break
        
        # Add quantity if available
        if 'quantity' in df.columns:
            agg_functions['quantity'] = 'sum'
        
        # Aggregate
        order_df = df.groupby('order_id').agg(agg_functions).reset_index()
        
        # Rename price column to order_total if needed
        for col in price_cols:
            if col in order_df.columns and col != 'order_total':
                order_df['order_total'] = order_df[col]
                break
        
        return order_df
    
    def _aggregate_by_customer_date(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate by customer + date (treats each customer-date as one order)."""
        
        # Create synthetic order_id
        df_temp = df.copy()
        df_temp['order_id'] = (
            df_temp['customer_id'].astype(str) + '_' + 
            df_temp['order_date'].dt.strftime('%Y%m%d')
        )
        
        # Find price column
        price_col = None
        for col in ['item_price', 'price', 'unit_price', 'order_total']:
            if col in df_temp.columns:
                price_col = col
                break
        
        if price_col is None:
            raise ValueError("No price column found for aggregation")
        
        # Aggregate
        agg_functions = {
            'order_date': 'first',
            'customer_id': 'first',
            price_col: 'sum'
        }
        
        # Add quantity if available
        if 'quantity' in df_temp.columns:
            agg_functions['quantity'] = 'sum'
        
        # Add other useful columns
        optional_cols = ['user_state', 'user_title', 'delivery_date']
        for col in optional_cols:
            if col in df_temp.columns:
                agg_functions[col] = 'first'
        
        order_df = df_temp.groupby('order_id').agg(agg_functions).reset_index()
        
        # Rename to canonical column
        order_df['order_total'] = order_df[price_col]
        
        # Add item count
        item_counts = df_temp.groupby('order_id').size().reset_index(name='item_count')
        order_df = order_df.merge(item_counts, on='order_id', how='left')
        
        return order_df
    
    def _aggregate_by_customer_date_sequential(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate by detecting order boundaries in sequential item data.
        Used for Germany data pattern where consecutive items from same customer
        on same date form one order.
        """
        df_temp = df.copy()
        
        # Sort by customer, date, and item_id
        sort_cols = ['customer_id', 'order_date']
        if 'order_item_id' in df_temp.columns:
            sort_cols.append('order_item_id')
        
        df_temp = df_temp.sort_values(sort_cols).reset_index(drop=True)
        
        # Detect order boundaries (new customer or date changes)
        df_temp['_customer_changed'] = (df_temp['customer_id'] != df_temp['customer_id'].shift(1))
        df_temp['_date_changed'] = (df_temp['order_date'] != df_temp['order_date'].shift(1))
        df_temp['_new_order'] = (df_temp['_customer_changed'] | df_temp['_date_changed'])
        
        # Create order_id by cumulative sum of new orders
        df_temp['order_id'] = df_temp['_new_order'].cumsum()
        df_temp['order_id'] = 'ORD_' + df_temp['order_id'].astype(str)
        
        # Find price column
        price_col = None
        for col in ['item_price', 'price', 'unit_price', 'order_total']:
            if col in df_temp.columns:
                price_col = col
                break
        
        if price_col is None:
            raise ValueError("No price column found for aggregation")
        
        # Aggregate by detected order_id
        agg_functions = {
            'order_date': 'first',
            'customer_id': 'first',
            price_col: 'sum'
        }
        
        # Add quantity if available
        if 'quantity' in df_temp.columns:
            agg_functions['quantity'] = 'sum'
        
        # Add optional columns
        optional_cols = ['user_state', 'user_title', 'delivery_date', 'user_dob', 'user_reg_date']
        for col in optional_cols:
            if col in df_temp.columns:
                agg_functions[col] = 'first'
        
        # Count returns if available
        if 'return' in df_temp.columns:
            agg_functions['return'] = 'sum'
        
        order_df = df_temp.groupby('order_id').agg(agg_functions).reset_index()
        
        # Rename to canonical column
        order_df['order_total'] = order_df[price_col]
        
        # Add metrics
        item_counts = df_temp.groupby('order_id').size().reset_index(name='item_count')
        order_df = order_df.merge(item_counts, on='order_id', how='left')
        
        # Calculate return rate if available
        if 'return' in order_df.columns:
            order_df['return_rate'] = order_df['return'] / order_df['item_count']
        
        logger.info(f"Created {len(order_df):,} orders from {len(df_temp):,} line items")
        logger.info(f"Average items per order: {order_df['item_count'].mean():.2f}")
        
        return order_df
    
    def get_aggregation_summary(self, df_original: pd.DataFrame, df_aggregated: pd.DataFrame) -> Dict[str, Any]:
        """Generate summary of aggregation results."""
        
        summary = {
            'original_rows': len(df_original),
            'aggregated_rows': len(df_aggregated),
            'reduction_ratio': len(df_original) / len(df_aggregated) if len(df_aggregated) > 0 else 0,
            'avg_items_per_order': len(df_original) / len(df_aggregated) if len(df_aggregated) > 0 else 0
        }
        
        if 'item_count' in df_aggregated.columns:
            summary['min_items_per_order'] = df_aggregated['item_count'].min()
            summary['max_items_per_order'] = df_aggregated['item_count'].max()
            summary['median_items_per_order'] = df_aggregated['item_count'].median()
        
        if 'order_total' in df_aggregated.columns:
            summary['total_revenue'] = df_aggregated['order_total'].sum()
            summary['avg_order_value'] = df_aggregated['order_total'].mean()
        
        return summary
