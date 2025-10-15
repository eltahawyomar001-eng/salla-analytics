"""Anomaly detection for revenue and order patterns in Salla analytics."""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from scipy import stats

logger = logging.getLogger(__name__)

class AnomalyDetector:
    """Detects anomalies in revenue and order patterns."""
    
    def __init__(self):
        self.z_threshold = 2.5  # Z-score threshold for anomaly detection
        self.iqr_factor = 1.5   # IQR factor for outlier detection
        self.min_data_points = 7  # Minimum data points needed for reliable detection
        
    def detect_anomalies(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Detect anomalies in revenue and order patterns.
        
        Args:
            df: DataFrame with order data (order_date, order_total, order_id)
            
        Returns:
            Dictionary containing anomaly detection results
        """
        # Validate required columns
        required_cols = ['order_date', 'order_total']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            logger.warning(f"Missing columns for anomaly detection: {missing_cols}")
            return self._get_empty_results()
        
        # Prepare data
        df_clean = self._prepare_data(df)
        
        if len(df_clean) < self.min_data_points:
            return {
                'insufficient_data': True,
                'message': f"Need at least {self.min_data_points} data points for anomaly detection",
                'data_points': len(df_clean)
            }
        
        logger.info(f"Detecting anomalies in {len(df_clean)} data points")
        
        # Daily level anomalies
        daily_anomalies = self._detect_daily_anomalies(df_clean)
        
        # Monthly level anomalies
        monthly_anomalies = self._detect_monthly_anomalies(df_clean)
        
        # Order value anomalies
        order_value_anomalies = self._detect_order_value_anomalies(df_clean)
        
        # Seasonal pattern anomalies
        seasonal_anomalies = self._detect_seasonal_anomalies(df_clean)
        
        # Get anomaly summary
        summary = self._get_anomaly_summary(daily_anomalies, monthly_anomalies, order_value_anomalies)
        
        results = {
            'daily_anomalies': daily_anomalies,
            'monthly_anomalies': monthly_anomalies,
            'order_value_anomalies': order_value_anomalies,
            'seasonal_anomalies': seasonal_anomalies,
            'summary': summary,
            'detection_params': {
                'z_threshold': self.z_threshold,
                'iqr_factor': self.iqr_factor,
                'min_data_points': self.min_data_points
            }
        }
        
        logger.info(f"Anomaly detection completed. Found {summary.get('total_anomalies', 0)} anomalies")
        
        return results
    
    def _prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare data for anomaly detection."""
        df_clean = df.copy()
        
        # Convert dates
        df_clean['order_date'] = pd.to_datetime(df_clean['order_date'])
        
        # Remove invalid data
        df_clean = df_clean[df_clean['order_total'] > 0]
        df_clean = df_clean[df_clean['order_date'].notna()]
        
        # Remove cancelled orders if status exists
        if 'order_status' in df_clean.columns:
            cancelled_statuses = ['cancelled', 'canceled', 'refunded', 'void']
            df_clean = df_clean[
                ~df_clean['order_status'].str.lower().isin(cancelled_statuses)
            ]
        
        # Sort by date
        df_clean = df_clean.sort_values('order_date')
        
        return df_clean
    
    def _detect_daily_anomalies(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect anomalies in daily revenue and order patterns."""
        # Aggregate by day
        daily_data = df.groupby(df['order_date'].dt.date).agg({
            'order_total': 'sum',
            'order_id': 'nunique' if 'order_id' in df.columns else 'count'
        }).round(2)
        
        daily_data.columns = ['daily_revenue', 'daily_orders']
        daily_data.index = pd.to_datetime(daily_data.index)
        
        if len(daily_data) < self.min_data_points:
            return {'insufficient_data': True}
        
        # Detect revenue anomalies
        revenue_anomalies = self._detect_statistical_anomalies(
            daily_data['daily_revenue'], 
            'daily_revenue'
        )
        
        # Detect order count anomalies
        orders_anomalies = self._detect_statistical_anomalies(
            daily_data['daily_orders'], 
            'daily_orders'
        )
        
        # Combine anomalies
        all_anomalies = []
        all_anomalies.extend(revenue_anomalies.get('anomalies', []))
        all_anomalies.extend(orders_anomalies.get('anomalies', []))
        
        # Sort by date
        all_anomalies.sort(key=lambda x: x['date'])
        
        return {
            'total_days': len(daily_data),
            'revenue_anomalies': revenue_anomalies,
            'orders_anomalies': orders_anomalies,
            'combined_anomalies': all_anomalies[:10],  # Top 10 most recent
            'data_range': {
                'start_date': daily_data.index.min(),
                'end_date': daily_data.index.max()
            }
        }
    
    def _detect_monthly_anomalies(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect anomalies in monthly revenue and order patterns."""
        # Aggregate by month
        monthly_data = df.groupby(df['order_date'].dt.to_period('M')).agg({
            'order_total': 'sum',
            'order_id': 'nunique' if 'order_id' in df.columns else 'count'
        }).round(2)
        
        monthly_data.columns = ['monthly_revenue', 'monthly_orders']
        monthly_data.index = pd.to_datetime(monthly_data.index.astype(str))
        
        if len(monthly_data) < 3:  # Need at least 3 months
            return {'insufficient_data': True}
        
        # Detect revenue anomalies
        revenue_anomalies = self._detect_statistical_anomalies(
            monthly_data['monthly_revenue'], 
            'monthly_revenue'
        )
        
        # Detect order count anomalies
        orders_anomalies = self._detect_statistical_anomalies(
            monthly_data['monthly_orders'], 
            'monthly_orders'
        )
        
        # Calculate month-over-month growth anomalies
        monthly_data['revenue_growth'] = monthly_data['monthly_revenue'].pct_change() * 100
        monthly_data['orders_growth'] = monthly_data['monthly_orders'].pct_change() * 100
        
        growth_anomalies = []
        if len(monthly_data) > 3:
            revenue_growth_anom = self._detect_statistical_anomalies(
                monthly_data['revenue_growth'].dropna(), 
                'revenue_growth'
            )
            growth_anomalies.extend(revenue_growth_anom.get('anomalies', []))
        
        return {
            'total_months': len(monthly_data),
            'revenue_anomalies': revenue_anomalies,
            'orders_anomalies': orders_anomalies,
            'growth_anomalies': growth_anomalies,
            'monthly_data': monthly_data.to_dict('index'),
            'data_range': {
                'start_month': monthly_data.index.min(),
                'end_month': monthly_data.index.max()
            }
        }
    
    def _detect_order_value_anomalies(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect anomalies in individual order values."""
        order_values = df['order_total'].copy()
        
        # Remove extreme outliers first (top and bottom 1%)
        p1, p99 = np.percentile(order_values, [1, 99])
        filtered_values = order_values[(order_values >= p1) & (order_values <= p99)]
        
        if len(filtered_values) < self.min_data_points:
            return {'insufficient_data': True}
        
        # Detect statistical anomalies
        anomalies = self._detect_statistical_anomalies(order_values, 'order_value')
        
        # Get extreme orders
        extreme_orders = []
        
        # Very high orders (top 1%)
        high_threshold = np.percentile(order_values, 99)
        high_orders = df[df['order_total'] >= high_threshold].copy()
        
        for _, order in high_orders.head(10).iterrows():
            extreme_orders.append({
                'type': 'high_value',
                'order_id': order.get('order_id', 'N/A'),
                'order_date': order['order_date'],
                'order_total': float(order['order_total']),
                'percentile': float(stats.percentileofscore(order_values, order['order_total'])),
                'z_score': float((order['order_total'] - order_values.mean()) / order_values.std())
            })
        
        # Very low orders (bottom 1%, but above 0)
        low_threshold = np.percentile(order_values[order_values > 0], 1)
        low_orders = df[(df['order_total'] <= low_threshold) & (df['order_total'] > 0)].copy()
        
        for _, order in low_orders.head(5).iterrows():
            extreme_orders.append({
                'type': 'low_value',
                'order_id': order.get('order_id', 'N/A'),
                'order_date': order['order_date'],
                'order_total': float(order['order_total']),
                'percentile': float(stats.percentileofscore(order_values, order['order_total'])),
                'z_score': float((order['order_total'] - order_values.mean()) / order_values.std())
            })
        
        return {
            'statistical_anomalies': anomalies,
            'extreme_orders': extreme_orders,
            'value_distribution': {
                'mean': float(order_values.mean()),
                'median': float(order_values.median()),
                'std': float(order_values.std()),
                'min': float(order_values.min()),
                'max': float(order_values.max()),
                'p1': float(p1),
                'p99': float(p99)
            }
        }
    
    def _detect_seasonal_anomalies(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect seasonal pattern anomalies."""
        if len(df) < 30:  # Need at least 30 days
            return {'insufficient_data': True}
        
        # Add time features
        df_seasonal = df.copy()
        df_seasonal['day_of_week'] = df_seasonal['order_date'].dt.dayofweek
        df_seasonal['day_of_month'] = df_seasonal['order_date'].dt.day
        df_seasonal['month'] = df_seasonal['order_date'].dt.month
        
        seasonal_patterns = {}
        
        # Day of week patterns
        dow_revenue = df_seasonal.groupby('day_of_week')['order_total'].sum()
        dow_anomalies = self._detect_statistical_anomalies(dow_revenue, 'day_of_week_revenue')
        seasonal_patterns['day_of_week'] = {
            'pattern': dow_revenue.to_dict(),
            'anomalies': dow_anomalies.get('anomalies', [])
        }
        
        # Monthly patterns (if data spans multiple years)
        if df_seasonal['order_date'].dt.year.nunique() > 1:
            monthly_revenue = df_seasonal.groupby('month')['order_total'].sum()
            monthly_anomalies = self._detect_statistical_anomalies(monthly_revenue, 'monthly_revenue')
            seasonal_patterns['monthly'] = {
                'pattern': monthly_revenue.to_dict(),
                'anomalies': monthly_anomalies.get('anomalies', [])
            }
        
        return seasonal_patterns
    
    def _detect_statistical_anomalies(
        self, 
        series: pd.Series, 
        metric_name: str
    ) -> Dict[str, Any]:
        """Detect statistical anomalies using multiple methods."""
        if len(series) < self.min_data_points:
            return {'insufficient_data': True}
        
        anomalies = []
        
        # Method 1: Z-score (modified using median and MAD for robustness)
        median = series.median()
        mad = np.median(np.abs(series - median))
        
        if mad > 0:
            modified_z_scores = 0.6745 * (series - median) / float(mad)
            
            # Find anomalies
            for i, (idx, value) in enumerate(series.items()):
                z_score_val = modified_z_scores.iloc[i]
                if abs(z_score_val) > self.z_threshold:
                    anomalies.append({
                        'date': idx if isinstance(idx, (datetime, pd.Timestamp)) else str(idx),
                        'value': float(value),
                        'metric': metric_name,
                        'method': 'modified_z_score',
                        'score': float(z_score_val),
                        'threshold': self.z_threshold,
                        'severity': 'high' if abs(z_score_val) > self.z_threshold * 1.5 else 'medium'
                    })
        
        # Method 2: IQR method
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        
        if IQR > 0:
            lower_bound = Q1 - self.iqr_factor * IQR
            upper_bound = Q3 + self.iqr_factor * IQR
            
            iqr_anomalies = series[(series < lower_bound) | (series > upper_bound)]
            
            for idx, value in iqr_anomalies.items():
                # Avoid duplicates from z-score method
                if not any(a['date'] == (idx if isinstance(idx, (datetime, pd.Timestamp)) else str(idx)) and a['method'] == 'modified_z_score' for a in anomalies):
                    distance_from_bounds = min(abs(value - lower_bound), abs(value - upper_bound))
                    severity = 'high' if distance_from_bounds > IQR else 'medium'
                    
                    anomalies.append({
                        'date': idx if isinstance(idx, (datetime, pd.Timestamp)) else str(idx),
                        'value': float(value),
                        'metric': metric_name,
                        'method': 'iqr',
                        'score': float(distance_from_bounds / IQR),
                        'threshold': self.iqr_factor,
                        'severity': severity
                    })
        
        # Sort by severity and score
        anomalies.sort(key=lambda x: (x['severity'] == 'high', abs(x['score'])), reverse=True)
        
        return {
            'total_anomalies': len(anomalies),
            'anomalies': anomalies[:10],  # Top 10 most significant
            'statistics': {
                'mean': float(series.mean()),
                'median': float(median),
                'std': float(series.std()),
                'mad': float(mad),
                'q1': float(Q1),
                'q3': float(Q3),
                'iqr': float(IQR)
            }
        }
    
    def _get_anomaly_summary(
        self, 
        daily_anomalies: Dict[str, Any], 
        monthly_anomalies: Dict[str, Any], 
        order_value_anomalies: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get overall summary of detected anomalies."""
        total_anomalies = 0
        anomaly_types = []
        
        # Count daily anomalies
        if 'combined_anomalies' in daily_anomalies:
            daily_count = len(daily_anomalies['combined_anomalies'])
            total_anomalies += daily_count
            if daily_count > 0:
                anomaly_types.append(f"{daily_count} daily pattern anomalies")
        
        # Count monthly anomalies
        if 'revenue_anomalies' in monthly_anomalies and 'total_anomalies' in monthly_anomalies['revenue_anomalies']:
            monthly_count = monthly_anomalies['revenue_anomalies']['total_anomalies']
            total_anomalies += monthly_count
            if monthly_count > 0:
                anomaly_types.append(f"{monthly_count} monthly pattern anomalies")
        
        # Count order value anomalies
        if 'extreme_orders' in order_value_anomalies:
            order_count = len(order_value_anomalies['extreme_orders'])
            total_anomalies += order_count
            if order_count > 0:
                anomaly_types.append(f"{order_count} extreme order values")
        
        # Get most recent anomalies
        recent_anomalies = []
        
        if 'combined_anomalies' in daily_anomalies:
            recent_anomalies.extend(daily_anomalies['combined_anomalies'][:3])
        
        if 'extreme_orders' in order_value_anomalies:
            recent_anomalies.extend(order_value_anomalies['extreme_orders'][:3])
        
        # Sort by date (most recent first)
        recent_anomalies.sort(
            key=lambda x: x.get('date', x.get('order_date', datetime.min)), 
            reverse=True
        )
        
        return {
            'total_anomalies': total_anomalies,
            'anomaly_types': anomaly_types,
            'recent_anomalies': recent_anomalies[:5],
            'has_anomalies': total_anomalies > 0,
            'severity_distribution': self._calculate_severity_distribution(recent_anomalies)
        }
    
    def _calculate_severity_distribution(self, anomalies: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate distribution of anomaly severities."""
        severity_counts = {'high': 0, 'medium': 0, 'low': 0}
        
        for anomaly in anomalies:
            severity = anomaly.get('severity', 'medium')
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        return severity_counts
    
    def _get_empty_results(self) -> Dict[str, Any]:
        """Return empty results structure."""
        return {
            'daily_anomalies': {'insufficient_data': True},
            'monthly_anomalies': {'insufficient_data': True},
            'order_value_anomalies': {'insufficient_data': True},
            'seasonal_anomalies': {'insufficient_data': True},
            'summary': {
                'total_anomalies': 0,
                'anomaly_types': [],
                'recent_anomalies': [],
                'has_anomalies': False
            }
        }

def detect_anomalies(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Convenience function to detect anomalies.
    
    Args:
        df: DataFrame with order data
        
    Returns:
        Anomaly detection results
    """
    detector = AnomalyDetector()
    return detector.detect_anomalies(df)