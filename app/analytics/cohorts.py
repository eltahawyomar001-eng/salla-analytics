"""Cohort analysis and customer retention metrics for Salla analytics."""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CohortAnalyzer:
    """Performs cohort analysis and retention calculations."""
    
    def __init__(self):
        self.min_cohort_size = 5  # Minimum customers per cohort for reliable analysis
        
    def perform_cohort_analysis(
        self, 
        df: pd.DataFrame,
        period: str = 'M'  # M for monthly, Q for quarterly
    ) -> Dict[str, Any]:
        """
        Perform comprehensive cohort analysis.
        
        Args:
            df: DataFrame with order data (customer_id, order_date, order_total)
            period: Cohort period ('M' for monthly, 'Q' for quarterly)
            
        Returns:
            Dictionary containing cohort analysis results
        """
        # Validate required columns
        required_cols = ['customer_id', 'order_date', 'order_total']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            raise ValueError(f"Missing required columns for cohort analysis: {missing_cols}")
        
        # Clean and prepare data
        df_clean = self._prepare_cohort_data(df)
        
        if len(df_clean) == 0:
            return self._get_empty_cohort_results()
        
        logger.info(f"Performing {period} cohort analysis for {df_clean['customer_id'].nunique()} customers")
        
        # Create cohort table
        cohort_table = self._create_cohort_table(df_clean, period)
        
        # Calculate retention matrix
        retention_matrix = self._calculate_retention_matrix(cohort_table)
        
        # Calculate cohort sizes
        cohort_sizes = self._calculate_cohort_sizes(cohort_table)
        
        # Calculate retention metrics
        retention_metrics = self._calculate_retention_metrics(retention_matrix, cohort_sizes)
        
        # Calculate time to second purchase
        second_purchase_metrics = self._calculate_second_purchase_metrics(df_clean)
        
        # Prepare visualization data
        viz_data = self._prepare_visualization_data(retention_matrix, cohort_sizes)
        
        results = {
            'cohort_table': cohort_table.to_dict(),
            'retention_matrix': retention_matrix.to_dict(),
            'cohort_sizes': cohort_sizes.to_dict(),
            'retention_metrics': retention_metrics,
            'second_purchase_metrics': second_purchase_metrics,
            'visualization_data': viz_data,
            'period': period,
            'total_cohorts': len(cohort_sizes),
            'analysis_summary': self._get_analysis_summary(retention_matrix, cohort_sizes)
        }
        
        logger.info(f"Cohort analysis completed: {len(cohort_sizes)} cohorts analyzed")
        
        return results
    
    def _prepare_cohort_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare data for cohort analysis."""
        df_clean = df.copy()
        
        # Convert dates
        df_clean['order_date'] = pd.to_datetime(df_clean['order_date'])
        
        # Remove invalid orders
        df_clean = df_clean[df_clean['order_total'] > 0]
        df_clean = df_clean[df_clean['order_date'].notna()]
        df_clean = df_clean[df_clean['customer_id'].astype(str).str.strip() != '']
        
        # Remove cancelled orders if status exists
        if 'order_status' in df_clean.columns:
            cancelled_statuses = ['cancelled', 'canceled', 'refunded', 'void']
            df_clean = df_clean[
                ~df_clean['order_status'].str.lower().isin(cancelled_statuses)
            ]
        
        # Sort by date
        df_clean = df_clean.sort_values('order_date')
        
        return df_clean
    
    def _create_cohort_table(self, df: pd.DataFrame, period: str) -> pd.DataFrame:
        """Create the base cohort table with customer acquisition and activity periods."""
        # Determine customer acquisition period (first order)
        customer_acquisition = df.groupby('customer_id')['order_date'].min().reset_index()
        customer_acquisition.columns = ['customer_id', 'acquisition_period']
        
        # Convert to period (monthly or quarterly)
        customer_acquisition['acquisition_period'] = customer_acquisition['acquisition_period'].dt.to_period(period)
        
        # Add acquisition period to main dataframe
        df_with_cohort = df.merge(customer_acquisition, on='customer_id')
        df_with_cohort['order_period'] = df_with_cohort['order_date'].dt.to_period(period)
        
        # Calculate period number (0 = acquisition period, 1 = next period, etc.)
        df_with_cohort['period_number'] = (
            df_with_cohort['order_period'] - df_with_cohort['acquisition_period']
        ).apply(attrgetter('n'))
        
        return df_with_cohort
    
    def _calculate_retention_matrix(self, cohort_table: pd.DataFrame) -> pd.DataFrame:
        """Calculate the retention matrix showing customer activity by cohort and period."""
        # Create matrix of unique customers per cohort and period
        cohort_data = cohort_table.groupby(['acquisition_period', 'period_number'])['customer_id'].nunique().reset_index()
        
        # Pivot to create matrix
        retention_matrix = cohort_data.pivot(
            index='acquisition_period', 
            columns='period_number', 
            values='customer_id'
        ).fillna(0)
        
        # Calculate retention rates (percentage of cohort size)
        cohort_sizes = retention_matrix.iloc[:, 0]  # Period 0 = cohort size
        
        retention_rates = retention_matrix.divide(cohort_sizes, axis=0)
        
        return retention_rates
    
    def _calculate_cohort_sizes(self, cohort_table: pd.DataFrame) -> pd.Series:
        """Calculate the size of each cohort."""
        return cohort_table.groupby('acquisition_period')['customer_id'].nunique()
    
    def _calculate_retention_metrics(
        self, 
        retention_matrix: pd.DataFrame, 
        cohort_sizes: pd.Series
    ) -> Dict[str, Any]:
        """Calculate various retention metrics."""
        metrics = {}
        
        if len(retention_matrix) == 0:
            return metrics
        
        # Overall retention rates by period
        period_retention = retention_matrix.mean(axis=0)
        metrics['avg_retention_by_period'] = period_retention.to_dict()
        
        # Cohort-specific metrics
        cohort_metrics = {}
        
        for cohort in retention_matrix.index:
            cohort_data = retention_matrix.loc[cohort]
            cohort_size_val = cohort_sizes.loc[cohort]
            
            # Skip small cohorts
            if cohort_size_val < self.min_cohort_size:
                continue
                
            cohort_metrics[str(cohort)] = {
                'cohort_size': int(cohort_size_val),
                'retention_rate_period_1': float(cohort_data.get(1, 0)) if len(cohort_data) > 1 else 0,
                'retention_rate_period_3': float(cohort_data.get(3, 0)) if len(cohort_data) > 3 else 0,
                'retention_rate_period_6': float(cohort_data.get(6, 0)) if len(cohort_data) > 6 else 0,
                'retention_rate_period_12': float(cohort_data.get(12, 0)) if len(cohort_data) > 12 else 0,
                'max_period': int(cohort_data.index.max()),
                'latest_retention': float(cohort_data.iloc[-1]) if len(cohort_data) > 0 else 0
            }
        
        metrics['cohort_metrics'] = cohort_metrics
        
        # Overall summary metrics
        valid_cohorts = [c for c in cohort_metrics.values() if c['cohort_size'] >= self.min_cohort_size]
        
        if valid_cohorts:
            metrics['summary'] = {
                'avg_retention_period_1': np.mean([c['retention_rate_period_1'] for c in valid_cohorts]),
                'avg_retention_period_3': np.mean([c['retention_rate_period_3'] for c in valid_cohorts if c['max_period'] >= 3]),
                'avg_retention_period_6': np.mean([c['retention_rate_period_6'] for c in valid_cohorts if c['max_period'] >= 6]),
                'avg_retention_period_12': np.mean([c['retention_rate_period_12'] for c in valid_cohorts if c['max_period'] >= 12]),
                'total_cohorts_analyzed': len(valid_cohorts)
            }
        
        return metrics
    
    def _calculate_second_purchase_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate time to second purchase metrics."""
        # Get customer order history
        customer_orders = df.groupby('customer_id')['order_date'].apply(list).reset_index()
        customer_orders['order_dates'] = customer_orders['order_date'].apply(lambda x: sorted(x))
        
        # Calculate time to second purchase
        second_purchase_times = []
        
        for _, row in customer_orders.iterrows():
            dates = row['order_dates']
            if len(dates) >= 2:
                time_diff = (dates[1] - dates[0]).days
                second_purchase_times.append(time_diff)
        
        if not second_purchase_times:
            return {'no_repeat_customers': True}
        
        second_purchase_times = np.array(second_purchase_times)
        
        metrics = {
            'total_repeat_customers': len(second_purchase_times),
            'avg_days_to_second_purchase': float(np.mean(second_purchase_times)),
            'median_days_to_second_purchase': float(np.median(second_purchase_times)),
            'min_days_to_second_purchase': int(np.min(second_purchase_times)),
            'max_days_to_second_purchase': int(np.max(second_purchase_times)),
            'std_days_to_second_purchase': float(np.std(second_purchase_times))
        }
        
        # Distribution buckets
        metrics['time_distribution'] = {
            'within_7_days': int(np.sum(second_purchase_times <= 7)),
            'within_30_days': int(np.sum(second_purchase_times <= 30)),
            'within_90_days': int(np.sum(second_purchase_times <= 90)),
            'within_180_days': int(np.sum(second_purchase_times <= 180)),
            'within_365_days': int(np.sum(second_purchase_times <= 365)),
            'over_365_days': int(np.sum(second_purchase_times > 365))
        }
        
        return metrics
    
    def _prepare_visualization_data(
        self, 
        retention_matrix: pd.DataFrame, 
        cohort_sizes: pd.Series
    ) -> Dict[str, Any]:
        """Prepare data for visualization components."""
        viz_data = {}
        
        if len(retention_matrix) == 0:
            return viz_data
        
        # Retention heatmap data
        viz_data['retention_heatmap'] = {
            'matrix': retention_matrix.round(3).values.tolist(),
            'cohort_labels': [str(idx) for idx in retention_matrix.index],
            'period_labels': [f"Period {i}" for i in retention_matrix.columns],
            'cohort_sizes': cohort_sizes.to_dict()
        }
        
        # Retention curves data
        retention_curves = {}
        for cohort in retention_matrix.index:
            cohort_size_val = cohort_sizes.loc[cohort]
            if cohort_size_val >= self.min_cohort_size:
                retention_curves[str(cohort)] = {
                    'periods': list(retention_matrix.columns),
                    'retention_rates': retention_matrix.loc[cohort].tolist(),
                    'cohort_size': int(cohort_size_val)
                }
        
        viz_data['retention_curves'] = retention_curves
        
        # Average retention curve
        if len(retention_matrix) > 0:
            avg_retention = retention_matrix.mean(axis=0)
            viz_data['average_retention_curve'] = {
                'periods': list(avg_retention.index),
                'retention_rates': avg_retention.tolist()
            }
        
        return viz_data
    
    def _get_analysis_summary(
        self, 
        retention_matrix: pd.DataFrame, 
        cohort_sizes: pd.Series
    ) -> Dict[str, Any]:
        """Get high-level summary of cohort analysis."""
        if len(retention_matrix) == 0:
            return {'insufficient_data': True}
        
        # Filter for reliable cohorts
        reliable_cohorts = cohort_sizes[cohort_sizes >= self.min_cohort_size]
        
        summary = {
            'total_cohorts': len(cohort_sizes),
            'reliable_cohorts': len(reliable_cohorts),
            'min_cohort_size_threshold': self.min_cohort_size,
            'largest_cohort_size': int(cohort_sizes.max()),
            'smallest_cohort_size': int(cohort_sizes.min()),
            'avg_cohort_size': float(cohort_sizes.mean()),
            'total_customers_analyzed': int(cohort_sizes.sum())
        }
        
        # Retention insights
        if len(reliable_cohorts) > 0:
            reliable_matrix = retention_matrix.loc[reliable_cohorts.index]
            
            # Period 1 retention (immediate repeat rate)
            if len(reliable_matrix.columns) > 1:
                period_1_retention = reliable_matrix.iloc[:, 1].mean()
                summary['avg_period_1_retention'] = float(period_1_retention)
                summary['period_1_retention_range'] = {
                    'min': float(reliable_matrix.iloc[:, 1].min()),
                    'max': float(reliable_matrix.iloc[:, 1].max())
                }
            
            # Long-term retention (if data available)
            if len(reliable_matrix.columns) > 6:
                period_6_retention = reliable_matrix.iloc[:, 6].mean()
                summary['avg_period_6_retention'] = float(period_6_retention)
        
        return summary
    
    def _get_empty_cohort_results(self) -> Dict[str, Any]:
        """Return empty results structure for invalid data."""
        return {
            'cohort_table': {},
            'retention_matrix': {},
            'cohort_sizes': {},
            'retention_metrics': {},
            'second_purchase_metrics': {'no_data': True},
            'visualization_data': {},
            'period': 'M',
            'total_cohorts': 0,
            'analysis_summary': {'insufficient_data': True}
        }

# Helper function for period number calculation
class attrgetter:
    def __init__(self, attr):
        self.attr = attr
    
    def __call__(self, obj):
        return getattr(obj, self.attr)

def perform_cohort_analysis(
    df: pd.DataFrame, 
    period: str = 'M'
) -> Dict[str, Any]:
    """
    Convenience function to perform cohort analysis.
    
    Args:
        df: DataFrame with order data
        period: Cohort period ('M' for monthly, 'Q' for quarterly)
        
    Returns:
        Cohort analysis results
    """
    analyzer = CohortAnalyzer()
    return analyzer.perform_cohort_analysis(df, period)