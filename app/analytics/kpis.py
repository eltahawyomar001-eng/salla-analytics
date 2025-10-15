"""Key Performance Indicators calculation for Salla analytics."""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class KPICalculator:
    """Calculates key performance indicators from Salla data."""
    
    def __init__(self):
        self.metrics_cache = {}
        
    def calculate_all_kpis(
        self,
        df: pd.DataFrame,
        currency: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive KPIs from order data.
        
        Args:
            df: DataFrame with mapped columns (order_id, order_date, customer_id, order_total, etc.)
            currency: Currency symbol for formatting (None for generic format)
            
        Returns:
            Dictionary containing all KPI metrics
        """
        # Validate required columns
        required_cols = ['order_id', 'order_date', 'customer_id', 'order_total']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Filter out invalid orders (cancelled, refunded, negative totals)
        df_clean = self._filter_valid_orders(df)
        
        if len(df_clean) == 0:
            return self._get_empty_kpis(currency)
        
        # Calculate core metrics
        kpis = {
            'currency': currency,
            'analysis_period': self._get_analysis_period(df_clean),
            'data_summary': self._get_data_summary(df_clean),
            'revenue_metrics': self._calculate_revenue_metrics(df_clean, currency),
            'customer_metrics': self._calculate_customer_metrics(df_clean),
            'order_metrics': self._calculate_order_metrics(df_clean),
            'trend_metrics': self._calculate_trend_metrics(df_clean),
            'product_metrics': self._calculate_product_metrics(df_clean),
            'growth_metrics': self._calculate_growth_metrics(df_clean)
        }
        
        # Calculate derived metrics
        kpis['derived_metrics'] = self._calculate_derived_metrics(kpis)
        
        return kpis
    
    def _filter_valid_orders(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter out cancelled, refunded, or invalid orders."""
        df_filtered = df.copy()
        
        # Remove orders with negative totals
        if 'order_total' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['order_total'] >= 0]
        
        # Remove cancelled orders if status column exists
        if 'order_status' in df_filtered.columns:
            cancelled_statuses = ['cancelled', 'canceled', 'refunded', 'void']
            df_filtered = df_filtered[
                ~df_filtered['order_status'].str.lower().isin(cancelled_statuses)
            ]
        
        # Remove orders with empty customer or order IDs
        for id_col in ['customer_id', 'order_id']:
            if id_col in df_filtered.columns:
                df_filtered = df_filtered[
                    df_filtered[id_col].astype(str).str.strip() != ''
                ]
        
        # Remove orders with invalid dates
        if 'order_date' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['order_date'].notna()]
        
        logger.info(f"Filtered data: {len(df)} -> {len(df_filtered)} orders")
        
        return df_filtered
    
    def _get_analysis_period(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get analysis period information."""
        if 'order_date' not in df.columns or len(df) == 0:
            return {}
        
        dates = pd.to_datetime(df['order_date'])
        
        return {
            'start_date': dates.min(),
            'end_date': dates.max(),
            'total_days': (dates.max() - dates.min()).days + 1,
            'total_months': len(dates.dt.to_period('M').unique()),
            'analysis_as_of': datetime.now()
        }
    
    def _get_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get basic data summary statistics."""
        return {
            'total_records': len(df),
            'unique_orders': df['order_id'].nunique() if 'order_id' in df.columns else 0,
            'unique_customers': df['customer_id'].nunique() if 'customer_id' in df.columns else 0,
            'unique_products': df['product_id'].nunique() if 'product_id' in df.columns else 0,
            'date_range_days': (
                (pd.to_datetime(df['order_date']).max() - pd.to_datetime(df['order_date']).min()).days + 1
                if 'order_date' in df.columns and len(df) > 0 else 0
            )
        }
    
    def _calculate_revenue_metrics(self, df: pd.DataFrame, currency: Optional[str]) -> Dict[str, Any]:
        """Calculate revenue-related metrics."""
        if 'order_total' not in df.columns:
            return {}
        
        # Aggregate by order to avoid double counting
        order_totals = df.groupby('order_id')['order_total'].first()
        
        revenue_stats = {
            'total_revenue': float(order_totals.sum()),
            'mean_revenue': float(order_totals.mean()),
            'median_revenue': float(order_totals.median()),
            'revenue_std': float(order_totals.std()),
            'min_order_value': float(order_totals.min()),
            'max_order_value': float(order_totals.max()),
            'currency': currency
        }
        
        # Revenue percentiles
        revenue_stats.update({
            'revenue_p25': float(order_totals.quantile(0.25)),
            'revenue_p75': float(order_totals.quantile(0.75)),
            'revenue_p90': float(order_totals.quantile(0.90)),
            'revenue_p95': float(order_totals.quantile(0.95))
        })
        
        # Revenue distribution
        revenue_stats['revenue_distribution'] = {
            'orders_under_100': int((order_totals < 100).sum()),
            'orders_100_500': int(((order_totals >= 100) & (order_totals < 500)).sum()),
            'orders_500_1000': int(((order_totals >= 500) & (order_totals < 1000)).sum()),
            'orders_over_1000': int((order_totals >= 1000).sum())
        }
        
        return revenue_stats
    
    def _calculate_customer_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate customer-related metrics."""
        if 'customer_id' not in df.columns:
            return {}
        
        # Customer order counts and revenue
        customer_stats = df.groupby('customer_id').agg({
            'order_id': 'nunique',
            'order_total': 'sum',
            'order_date': ['min', 'max']
        }).round(2)
        
        customer_stats.columns = ['order_count', 'total_spent', 'first_order', 'last_order']
        
        metrics = {
            'total_customers': len(customer_stats),
            'new_customers': int((customer_stats['order_count'] == 1).sum()),
            'returning_customers': int((customer_stats['order_count'] > 1).sum()),
            'repeat_rate': float((customer_stats['order_count'] > 1).mean() * 100),
            'avg_orders_per_customer': float(customer_stats['order_count'].mean()),
            'median_orders_per_customer': float(customer_stats['order_count'].median()),
            'max_orders_per_customer': int(customer_stats['order_count'].max()),
            'avg_customer_value': float(customer_stats['total_spent'].mean()),
            'median_customer_value': float(customer_stats['total_spent'].median())
        }
        
        # Customer lifecycle metrics
        if 'order_date' in df.columns:
            # Calculate days between first and last order for returning customers
            returning_customers = customer_stats[customer_stats['order_count'] > 1].copy()
            if len(returning_customers) > 0:
                returning_customers['customer_lifespan'] = (
                    pd.to_datetime(returning_customers['last_order']) - 
                    pd.to_datetime(returning_customers['first_order'])
                ).dt.days
                
                metrics['avg_customer_lifespan_days'] = float(
                    returning_customers['customer_lifespan'].mean()
                )
                metrics['median_customer_lifespan_days'] = float(
                    returning_customers['customer_lifespan'].median()
                )
        
        # Customer value distribution
        metrics['customer_value_distribution'] = {
            'customers_under_100': int((customer_stats['total_spent'] < 100).sum()),
            'customers_100_500': int(((customer_stats['total_spent'] >= 100) & (customer_stats['total_spent'] < 500)).sum()),
            'customers_500_1000': int(((customer_stats['total_spent'] >= 500) & (customer_stats['total_spent'] < 1000)).sum()),
            'customers_over_1000': int((customer_stats['total_spent'] >= 1000).sum())
        }
        
        return metrics
    
    def _calculate_order_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate order-related metrics."""
        # Aggregate by order to get unique orders
        agg_dict = {
            'order_total': 'first',
            'customer_id': 'first',
            'order_date': 'first'
        }
        
        # Only include product columns if they exist
        if 'product_id' in df.columns:
            agg_dict['product_id'] = 'nunique'
        if 'quantity' in df.columns:
            agg_dict['quantity'] = 'sum'
            
        order_data = df.groupby('order_id').agg(agg_dict).round(2)
        
        metrics = {
            'total_orders': len(order_data),
            'average_order_value': float(order_data['order_total'].mean()),
            'median_order_value': float(order_data['order_total'].median()),
            'orders_per_day': 0,
            'avg_items_per_order': float(order_data['product_id'].mean()) if 'product_id' in order_data.columns else 1,
            'avg_quantity_per_order': float(order_data['quantity'].mean()) if 'quantity' in order_data.columns else 1
        }
        
        # Calculate orders per day
        if 'order_date' in df.columns and len(order_data) > 0:
            date_range = (
                pd.to_datetime(order_data['order_date']).max() - 
                pd.to_datetime(order_data['order_date']).min()
            ).days + 1
            
            metrics['orders_per_day'] = float(len(order_data) / max(1, date_range))
        
        return metrics
    
    def _calculate_trend_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate trend and time-based metrics."""
        if 'order_date' not in df.columns:
            return {}
        
        # Convert to datetime
        df_trend = df.copy()
        df_trend['order_date'] = pd.to_datetime(df_trend['order_date'])
        
        # Monthly trends
        monthly_data = df_trend.groupby([
            df_trend['order_date'].dt.to_period('M'), 'order_id'
        ])['order_total'].first().reset_index()
        
        monthly_summary = monthly_data.groupby('order_date').agg({
            'order_total': ['sum', 'count', 'mean']
        }).round(2)
        
        monthly_summary.columns = ['revenue', 'orders', 'aov']
        monthly_summary.index = monthly_summary.index.astype(str)
        
        # Daily trends (last 30 days)
        recent_date = df_trend['order_date'].max()
        last_30_days = df_trend[
            df_trend['order_date'] >= (recent_date - timedelta(days=30))
        ]
        
        daily_data = last_30_days.groupby([
            last_30_days['order_date'].dt.date, 'order_id'
        ])['order_total'].first().reset_index()
        
        daily_summary = daily_data.groupby('order_date').agg({
            'order_total': ['sum', 'count']
        }).round(2)
        
        daily_summary.columns = ['revenue', 'orders']
        daily_summary.index = daily_summary.index.astype(str)
        
        return {
            'monthly_trends': monthly_summary.to_dict('index'),
            'daily_trends_last_30': daily_summary.to_dict('index'),
            'trend_period_months': len(monthly_summary),
            'latest_month_revenue': float(monthly_summary['revenue'].iloc[-1]) if len(monthly_summary) > 0 else 0,
            'latest_month_orders': int(monthly_summary['orders'].iloc[-1]) if len(monthly_summary) > 0 else 0
        }
    
    def _calculate_product_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate product-related metrics."""
        if 'product_id' not in df.columns:
            return {}
        
        # Product performance
        product_data = df.groupby('product_id').agg({
            'order_total': 'sum',
            'order_id': 'nunique',
            'customer_id': 'nunique',
            'quantity': 'sum' if 'quantity' in df.columns else 'count'
        }).round(2)
        
        product_data.columns = ['revenue', 'orders', 'customers', 'quantity']
        
        metrics = {
            'total_products': len(product_data),
            'avg_revenue_per_product': float(product_data['revenue'].mean()),
            'top_products_by_revenue': product_data.nlargest(10, 'revenue')['revenue'].to_dict(),
            'top_products_by_orders': product_data.nlargest(10, 'orders')['orders'].to_dict(),
            'top_products_by_customers': product_data.nlargest(10, 'customers')['customers'].to_dict()
        }
        
        return metrics
    
    def _calculate_growth_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate growth and comparison metrics."""
        if 'order_date' not in df.columns or len(df) < 2:
            return {}
        
        df_growth = df.copy()
        df_growth['order_date'] = pd.to_datetime(df_growth['order_date'])
        
        # Get monthly data
        monthly_data = df_growth.groupby([
            df_growth['order_date'].dt.to_period('M'), 'order_id'
        ])['order_total'].first().reset_index()
        
        monthly_summary = monthly_data.groupby('order_date').agg({
            'order_total': ['sum', 'count']
        })
        
        monthly_summary.columns = ['revenue', 'orders']
        
        if len(monthly_summary) < 2:
            return {}
        
        # Calculate month-over-month growth
        monthly_summary['revenue_growth'] = monthly_summary['revenue'].pct_change() * 100
        monthly_summary['orders_growth'] = monthly_summary['orders'].pct_change() * 100
        
        # Get recent growth metrics
        latest_growth = {
            'latest_month_revenue_growth': float(monthly_summary['revenue_growth'].iloc[-1]) 
                if not pd.isna(monthly_summary['revenue_growth'].iloc[-1]) else 0,
            'latest_month_orders_growth': float(monthly_summary['orders_growth'].iloc[-1])
                if not pd.isna(monthly_summary['orders_growth'].iloc[-1]) else 0,
            'avg_monthly_revenue_growth': float(monthly_summary['revenue_growth'].mean())
                if not monthly_summary['revenue_growth'].isna().all() else 0,
            'avg_monthly_orders_growth': float(monthly_summary['orders_growth'].mean())
                if not monthly_summary['orders_growth'].isna().all() else 0
        }
        
        return latest_growth
    
    def _calculate_derived_metrics(self, kpis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate derived metrics from base KPIs."""
        derived = {}
        
        # Revenue metrics
        revenue = kpis.get('revenue_metrics', {})
        customer = kpis.get('customer_metrics', {})
        order = kpis.get('order_metrics', {})
        
        # Customer acquisition metrics
        if customer:
            total_customers = customer.get('total_customers', 0)
            new_customers = customer.get('new_customers', 0)
            
            if total_customers > 0:
                derived['new_customer_percentage'] = float((new_customers / total_customers) * 100)
                derived['returning_customer_percentage'] = float(100 - derived['new_customer_percentage'])
        
        # Revenue per customer
        if revenue and customer:
            total_revenue = revenue.get('total_revenue', 0)
            total_customers = customer.get('total_customers', 0)
            
            if total_customers > 0:
                derived['revenue_per_customer'] = float(total_revenue / total_customers)
        
        # Order frequency
        if order and customer:
            total_orders = order.get('total_orders', 0)
            total_customers = customer.get('total_customers', 0)
            
            if total_customers > 0:
                derived['orders_per_customer'] = float(total_orders / total_customers)
        
        return derived
    
    def _get_empty_kpis(self, currency: Optional[str]) -> Dict[str, Any]:
        """Return empty KPI structure for invalid data."""
        return {
            'currency': currency,
            'analysis_period': {},
            'data_summary': {
                'total_records': 0,
                'unique_orders': 0,
                'unique_customers': 0,
                'unique_products': 0
            },
            'revenue_metrics': {'total_revenue': 0, 'currency': currency},
            'customer_metrics': {'total_customers': 0, 'repeat_rate': 0},
            'order_metrics': {'total_orders': 0, 'average_order_value': 0},
            'trend_metrics': {},
            'product_metrics': {},
            'growth_metrics': {},
            'derived_metrics': {}
        }
    
    def get_kpi_summary(self, kpis: Dict[str, Any]) -> Dict[str, Any]:
        """Get a summary of the most important KPIs."""
        summary = {}
        
        # Extract key metrics
        if 'revenue_metrics' in kpis:
            summary['total_revenue'] = kpis['revenue_metrics'].get('total_revenue', 0)
            summary['currency'] = kpis['revenue_metrics'].get('currency')
        
        if 'order_metrics' in kpis:
            summary['total_orders'] = kpis['order_metrics'].get('total_orders', 0)
            summary['average_order_value'] = kpis['order_metrics'].get('average_order_value', 0)
        
        if 'customer_metrics' in kpis:
            summary['total_customers'] = kpis['customer_metrics'].get('total_customers', 0)
            summary['repeat_rate'] = kpis['customer_metrics'].get('repeat_rate', 0)
        
        if 'derived_metrics' in kpis:
            summary['orders_per_customer'] = kpis['derived_metrics'].get('orders_per_customer', 0)
            summary['revenue_per_customer'] = kpis['derived_metrics'].get('revenue_per_customer', 0)
        
        return summary

def calculate_kpis(df: pd.DataFrame, currency: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to calculate KPIs.
    
    Args:
        df: DataFrame with order data
        currency: Currency symbol (None for generic format)
        
    Returns:
        KPI metrics dictionary
    """
    calculator = KPICalculator()
    return calculator.calculate_all_kpis(df, currency)