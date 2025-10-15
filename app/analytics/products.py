"""Product analysis and market basket insights for Salla analytics."""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from itertools import combinations
from collections import Counter

logger = logging.getLogger(__name__)

class ProductAnalyzer:
    """Analyzes product performance and customer purchasing patterns."""
    
    def __init__(self):
        self.min_support_threshold = 0.01  # 1% minimum support for association rules
        self.min_confidence_threshold = 0.1  # 10% minimum confidence
        
    def analyze_products(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform comprehensive product analysis.
        
        Args:
            df: DataFrame with product data (product_id, product_name, order_total, quantity, etc.)
            
        Returns:
            Dictionary containing product analysis results
        """
        # Check for required columns
        if 'product_name' not in df.columns and 'product_id' not in df.columns:
            logger.warning("No product columns found - skipping product analysis")
            return self._get_empty_results()
        
        # Use product_name if product_id not available
        if 'product_id' not in df.columns and 'product_name' in df.columns:
            df = df.copy()
            df['product_id'] = df['product_name']
            logger.info("Using product_name as product_id")
        
        if 'product_id' not in df.columns:
            logger.warning("No product identification columns found - skipping product analysis")
            return self._get_empty_results()
        
        # Clean and prepare data
        df_clean = self._prepare_product_data(df)
        
        if len(df_clean) == 0:
            return self._get_empty_results()
        
        logger.info(f"Analyzing {df_clean['product_id'].nunique()} unique products")
        
        # Calculate product performance metrics
        product_performance = self._calculate_product_performance(df_clean)
        
        # Calculate category analysis if available
        category_analysis = self._analyze_categories(df_clean)
        
        # Perform market basket analysis
        market_basket = self._perform_market_basket_analysis(df_clean)
        
        # Calculate product lifecycle metrics
        lifecycle_metrics = self._calculate_lifecycle_metrics(df_clean)
        
        # Get top performers
        top_products = self._get_top_products(product_performance)
        
        results = {
            'product_performance': product_performance.to_dict('index'),
            'category_analysis': category_analysis,
            'market_basket': market_basket,
            'lifecycle_metrics': lifecycle_metrics,
            'top_products': top_products,
            'summary_stats': self._get_summary_stats(df_clean, product_performance),
            'total_products': len(product_performance)
        }
        
        logger.info(f"Product analysis completed for {len(product_performance)} products")
        
        return results
    
    def _prepare_product_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare product data for analysis."""
        df_clean = df.copy()
        
        # Ensure product_id exists (should be guaranteed by analyze_products check)
        if 'product_id' not in df_clean.columns:
            if 'product_name' in df_clean.columns:
                df_clean['product_id'] = df_clean['product_name']
            else:
                logger.warning("No product identification columns - cannot prepare product data")
                return pd.DataFrame()  # Return empty dataframe
        
        # Remove invalid orders
        if 'order_total' in df_clean.columns:
            df_clean = df_clean[df_clean['order_total'] > 0]
        
        # Remove empty product IDs
        df_clean = df_clean[df_clean['product_id'].astype(str).str.strip() != '']
        
        # Handle missing product names
        if 'product_name' not in df_clean.columns:
            df_clean['product_name'] = df_clean['product_id'].astype(str)
        else:
            df_clean['product_name'] = df_clean['product_name'].fillna(df_clean['product_id'].astype(str))
        
        # Handle missing quantities
        if 'quantity' not in df_clean.columns:
            logger.info("Adding default quantity column (value=1) for product analysis")
            df_clean['quantity'] = 1
        else:
            df_clean['quantity'] = df_clean['quantity'].fillna(1)
            df_clean = df_clean[df_clean['quantity'] > 0]
        
        # Calculate item totals if missing
        if 'item_total' not in df_clean.columns:
            if 'order_total' in df_clean.columns:
                # Estimate item total as order total (rough approximation)
                logger.info("Using order_total as item_total for product analysis")
                df_clean['item_total'] = df_clean['order_total']
            else:
                df_clean['item_total'] = 0
        
        return df_clean
    
    def _calculate_product_performance(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate comprehensive product performance metrics."""
        # Ensure required columns exist
        agg_dict = {
            'order_id': 'nunique',  # Number of orders
            'customer_id': 'nunique' if 'customer_id' in df.columns else 'count',  # Number of unique customers
        }
        
        if 'quantity' in df.columns:
            agg_dict['quantity'] = 'sum'  # Total quantity sold
        
        if 'item_total' in df.columns:
            agg_dict['item_total'] = 'sum'  # Total revenue
        elif 'order_total' in df.columns:
            agg_dict['order_total'] = 'sum'  # Use order_total as fallback
        
        if 'order_date' in df.columns:
            agg_dict['order_date'] = ['min', 'max']  # type: ignore
        
        # Group by product
        product_metrics = df.groupby(['product_id', 'product_name']).agg(agg_dict).round(2)
        
        # Flatten column names
        col_names = ['orders', 'customers']
        if 'quantity' in agg_dict:
            col_names.append('quantity_sold')
        if 'item_total' in agg_dict:
            col_names.append('revenue')
        elif 'order_total' in agg_dict:
            col_names.append('revenue')
        if 'order_date' in agg_dict:
            col_names.extend(['first_sale', 'last_sale'])
        
        product_metrics.columns = col_names
        
        # Calculate derived metrics only if base columns exist
        if 'quantity_sold' in product_metrics.columns:
            product_metrics['avg_quantity_per_order'] = product_metrics['quantity_sold'] / product_metrics['orders']
        
        if 'revenue' in product_metrics.columns:
            product_metrics['avg_revenue_per_order'] = product_metrics['revenue'] / product_metrics['orders']
            product_metrics['avg_revenue_per_customer'] = product_metrics['revenue'] / product_metrics['customers']
            
            if 'customer_id' in df.columns:
                product_metrics['customer_penetration'] = product_metrics['customers'] / df['customer_id'].nunique()
            
            # Calculate price per unit
            if 'quantity_sold' in product_metrics.columns:
                product_metrics['avg_price_per_unit'] = product_metrics['revenue'] / product_metrics['quantity_sold']
        
        # Product lifecycle metrics
        if 'order_date' in df.columns:
            product_metrics['days_on_market'] = (
                pd.to_datetime(product_metrics['last_sale']) - 
                pd.to_datetime(product_metrics['first_sale'])
            ).dt.days + 1
            
            product_metrics['avg_orders_per_day'] = product_metrics['orders'] / product_metrics['days_on_market']
        
        # Reset index to make product_id and product_name regular columns
        product_metrics = product_metrics.reset_index()
        
        return product_metrics
    
    def _analyze_categories(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze product categories if category information is available."""
        category_analysis = {}
        
        # Check if category column exists
        category_col = None
        for col in ['category', 'product_category', 'category_name']:
            if col in df.columns:
                category_col = col
                break
        
        if category_col is None:
            category_analysis['available'] = False
            category_analysis['message'] = "No category information found"
            return category_analysis
        
        # Analyze categories
        df_cat = df.copy()
        df_cat[category_col] = df_cat[category_col].fillna('Unknown')
        
        category_stats = df_cat.groupby(category_col).agg({
            'product_id': 'nunique',
            'order_id': 'nunique',
            'customer_id': 'nunique',
            'quantity': 'sum' if 'quantity' in df_cat.columns else 'count',
            'item_total': 'sum' if 'item_total' in df_cat.columns else 'count'
        }).round(2)
        
        category_stats.columns = ['unique_products', 'orders', 'customers', 'quantity_sold', 'revenue']
        
        # Calculate category performance metrics
        category_stats['avg_revenue_per_product'] = category_stats['revenue'] / category_stats['unique_products']
        category_stats['avg_orders_per_product'] = category_stats['orders'] / category_stats['unique_products']
        
        category_analysis = {
            'available': True,
            'total_categories': len(category_stats),
            'category_performance': category_stats.to_dict('index'),
            'top_categories_by_revenue': category_stats.nlargest(10, 'revenue').to_dict('index'),
            'top_categories_by_orders': category_stats.nlargest(10, 'orders').to_dict('index')
        }
        
        return category_analysis
    
    def _perform_market_basket_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform market basket analysis to find product associations."""
        market_basket = {
            'available': False,
            'message': "Insufficient data for market basket analysis"
        }
        
        if 'order_id' not in df.columns:
            return market_basket
        
        # Create order-product matrix
        order_products = df.groupby('order_id')['product_id'].apply(list).reset_index()
        order_products['product_count'] = order_products['product_id'].apply(len)
        
        # Filter orders with multiple products
        multi_product_orders = order_products[order_products['product_count'] > 1]
        
        if len(multi_product_orders) < 10:  # Need at least 10 multi-product orders
            return market_basket
        
        # Calculate product pairs
        product_pairs = []
        for _, row in multi_product_orders.iterrows():
            products = row['product_id']
            pairs = list(combinations(sorted(products), 2))
            product_pairs.extend(pairs)
        
        if len(product_pairs) == 0:
            return market_basket
        
        # Count pair frequencies
        pair_counts = Counter(product_pairs)
        total_orders = len(order_products)
        
        # Calculate association metrics
        associations = []
        for (product_a, product_b), count in pair_counts.most_common(50):  # Top 50 pairs
            # Calculate support
            support = count / total_orders
            
            if support < self.min_support_threshold:
                continue
            
            # Calculate confidence A -> B and B -> A
            orders_with_a = len(order_products[order_products['product_id'].apply(lambda x: product_a in x)])
            orders_with_b = len(order_products[order_products['product_id'].apply(lambda x: product_b in x)])
            
            confidence_a_to_b = count / orders_with_a if orders_with_a > 0 else 0
            confidence_b_to_a = count / orders_with_b if orders_with_b > 0 else 0
            
            # Calculate lift
            expected_ab = (orders_with_a / total_orders) * (orders_with_b / total_orders)
            lift = support / expected_ab if expected_ab > 0 else 0
            
            if confidence_a_to_b >= self.min_confidence_threshold or confidence_b_to_a >= self.min_confidence_threshold:
                associations.append({
                    'product_a': product_a,
                    'product_b': product_b,
                    'support': round(support, 4),
                    'confidence_a_to_b': round(confidence_a_to_b, 4),
                    'confidence_b_to_a': round(confidence_b_to_a, 4),
                    'lift': round(lift, 4),
                    'frequency': count
                })
        
        if associations:
            market_basket = {
                'available': True,
                'total_associations': len(associations),
                'associations': associations[:20],  # Top 20 associations
                'total_multi_product_orders': len(multi_product_orders),
                'total_orders_analyzed': total_orders,
                'thresholds': {
                    'min_support': self.min_support_threshold,
                    'min_confidence': self.min_confidence_threshold
                }
            }
        
        return market_basket
    
    def _calculate_lifecycle_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate product lifecycle metrics."""
        lifecycle = {}
        
        if 'order_date' not in df.columns:
            lifecycle['available'] = False
            return lifecycle
        
        # Convert dates
        df_lc = df.copy()
        df_lc['order_date'] = pd.to_datetime(df_lc['order_date'])
        
        # Product introduction dates
        product_intro = df_lc.groupby('product_id')['order_date'].min()
        
        # Recent activity (last 30 days)
        recent_date = df_lc['order_date'].max()
        cutoff_date = recent_date - pd.Timedelta(days=30)
        
        recent_products = df_lc[df_lc['order_date'] >= cutoff_date]['product_id'].unique()
        
        # Product performance over time
        monthly_performance = df_lc.groupby([
            df_lc['order_date'].dt.to_period('M'),
            'product_id'
        ]).agg({
            'quantity': 'sum' if 'quantity' in df_lc.columns else 'count',
            'item_total': 'sum' if 'item_total' in df_lc.columns else 'count'
        }).reset_index()
        
        lifecycle = {
            'available': True,
            'total_products_introduced': len(product_intro),
            'products_active_last_30_days': len(recent_products),
            'oldest_product_date': product_intro.min(),
            'newest_product_date': product_intro.max(),
            'monthly_performance_data': monthly_performance.to_dict('records')
        }
        
        return lifecycle
    
    def _get_top_products(self, product_performance: pd.DataFrame) -> Dict[str, Any]:
        """Get top performing products across different metrics."""
        if len(product_performance) == 0:
            return {}
        
        top_products = {
            'by_revenue': product_performance.nlargest(10, 'revenue')[['product_id', 'product_name', 'revenue']].to_dict('records'),
            'by_quantity': product_performance.nlargest(10, 'quantity_sold')[['product_id', 'product_name', 'quantity_sold']].to_dict('records'),
            'by_orders': product_performance.nlargest(10, 'orders')[['product_id', 'product_name', 'orders']].to_dict('records'),
            'by_customers': product_performance.nlargest(10, 'customers')[['product_id', 'product_name', 'customers']].to_dict('records'),
            'by_avg_price': product_performance.nlargest(10, 'avg_price_per_unit')[['product_id', 'product_name', 'avg_price_per_unit']].to_dict('records')
        }
        
        return top_products
    
    def _get_summary_stats(self, df: pd.DataFrame, product_performance: pd.DataFrame) -> Dict[str, Any]:
        """Get summary statistics for product analysis."""
        if len(product_performance) == 0:
            return {}
        
        summary = {
            'total_products': len(product_performance),
            'total_quantity_sold': int(product_performance['quantity_sold'].sum()),
            'total_revenue': float(product_performance['revenue'].sum()),
            'avg_revenue_per_product': float(product_performance['revenue'].mean()),
            'median_revenue_per_product': float(product_performance['revenue'].median()),
            'avg_orders_per_product': float(product_performance['orders'].mean()),
            'median_orders_per_product': float(product_performance['orders'].median()),
            'products_with_single_order': int((product_performance['orders'] == 1).sum()),
            'products_with_multiple_orders': int((product_performance['orders'] > 1).sum())
        }
        
        # Revenue distribution
        summary['revenue_distribution'] = {
            'top_10_percent_revenue_share': float(
                product_performance.nlargest(max(1, len(product_performance) // 10), 'revenue')['revenue'].sum() / 
                product_performance['revenue'].sum() * 100
            ),
            'top_20_percent_revenue_share': float(
                product_performance.nlargest(max(1, len(product_performance) // 5), 'revenue')['revenue'].sum() / 
                product_performance['revenue'].sum() * 100
            )
        }
        
        return summary
    
    def _get_limited_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Return limited analysis when product_id is not available."""
        return {
            'limited_analysis': True,
            'message': "Product analysis requires product_id column",
            'available_columns': list(df.columns),
            'total_records': len(df)
        }
    
    def _get_empty_results(self) -> Dict[str, Any]:
        """Return empty results structure."""
        return {
            'product_performance': {},
            'category_analysis': {'available': False},
            'market_basket': {'available': False},
            'lifecycle_metrics': {'available': False},
            'top_products': {},
            'summary_stats': {},
            'total_products': 0
        }

def analyze_products(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Convenience function to perform product analysis.
    
    Args:
        df: DataFrame with product data
        
    Returns:
        Product analysis results
    """
    analyzer = ProductAnalyzer()
    return analyzer.analyze_products(df)