"""RFM (Recency, Frequency, Monetary) analysis for customer segmentation."""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta

from ..config import RFM_SEGMENTS

logger = logging.getLogger(__name__)

class RFMAnalyzer:
    """Performs RFM analysis and customer segmentation."""
    
    def __init__(self):
        self.segments = RFM_SEGMENTS
        
    def calculate_rfm_scores(
        self, 
        df: pd.DataFrame, 
        analysis_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Calculate RFM scores for each customer.
        
        Formula explanations:
        - Recency: Days since last order (lower is better)
        - Frequency: Number of distinct orders (higher is better)  
        - Monetary: Total revenue per customer (higher is better)
        
        Args:
            df: DataFrame with order data (must have customer_id, order_date, order_total)
            analysis_date: Date to calculate recency from (defaults to max order date)
            
        Returns:
            DataFrame with customer RFM scores and segments
        """
        # Validate required columns
        required_cols = ['customer_id', 'order_date', 'order_total']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            raise ValueError(f"Missing required columns for RFM analysis: {missing_cols}")
        
        # Filter valid orders
        df_clean = self._filter_valid_orders(df)
        
        if len(df_clean) == 0:
            return pd.DataFrame()
        
        # Set analysis date
        if analysis_date is None:
            analysis_date = pd.to_datetime(df_clean['order_date']).max()
        
        logger.info(f"Calculating RFM scores for {df_clean['customer_id'].nunique()} customers")
        logger.info(f"Analysis date: {analysis_date}")
        
        # Calculate RFM metrics per customer
        rfm_data = self._calculate_customer_metrics(df_clean, analysis_date)
        
        # Calculate quintile scores (1-5 scale)
        rfm_scores = self._calculate_quintile_scores(rfm_data)
        
        # Assign segments based on RFM scores
        rfm_segments = self._assign_segments(rfm_scores)
        
        # Add segment metadata
        rfm_final = self._add_segment_metadata(rfm_segments)
        
        logger.info(f"RFM analysis completed for {len(rfm_final)} customers")
        
        return rfm_final
    
    def _filter_valid_orders(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter out invalid orders for RFM analysis."""
        df_filtered = df.copy()
        
        # Remove orders with zero or negative totals
        df_filtered = df_filtered[df_filtered['order_total'] > 0]
        
        # Remove invalid dates
        df_filtered = df_filtered[pd.to_datetime(df_filtered['order_date']).notna()]
        
        # Remove empty customer IDs
        df_filtered = df_filtered[
            df_filtered['customer_id'].astype(str).str.strip() != ''
        ]
        
        # Remove cancelled/refunded orders if status exists
        if 'order_status' in df_filtered.columns:
            cancelled_statuses = ['cancelled', 'canceled', 'refunded', 'void']
            df_filtered = df_filtered[
                ~df_filtered['order_status'].str.lower().isin(cancelled_statuses)
            ]
        
        return df_filtered
    
    def _calculate_customer_metrics(
        self, 
        df: pd.DataFrame, 
        analysis_date: datetime
    ) -> pd.DataFrame:
        """Calculate raw RFM metrics for each customer."""
        # Ensure order_date is datetime
        df['order_date'] = pd.to_datetime(df['order_date'])
        
        # Group by customer and calculate metrics
        customer_metrics = df.groupby('customer_id').agg({
            'order_date': ['max', 'count'],  # Last order date, frequency
            'order_total': 'sum',  # Total monetary value
            'order_id': 'nunique'  # Distinct order count (frequency alternative)
        }).round(2)
        
        # Flatten column names
        customer_metrics.columns = ['last_order_date', 'order_count', 'total_spent', 'distinct_orders']
        
        # Use distinct orders as frequency (more accurate than row count)
        customer_metrics['frequency'] = customer_metrics['distinct_orders']
        
        # Calculate recency in days
        customer_metrics['recency_days'] = customer_metrics['last_order_date'].apply(
            lambda x: (analysis_date - x).days
        )
        
        # Ensure recency is not negative (future orders)
        customer_metrics['recency_days'] = customer_metrics['recency_days'].clip(lower=0)
        
        # Rename for clarity
        customer_metrics = customer_metrics.rename(columns={
            'total_spent': 'monetary',
            'recency_days': 'recency'
        })
        
        # Select final RFM columns
        rfm_metrics = customer_metrics[['recency', 'frequency', 'monetary', 'last_order_date']].copy()
        
        logger.info(f"RFM metrics calculated:")
        logger.info(f"- Recency range: {rfm_metrics['recency'].min():.0f} to {rfm_metrics['recency'].max():.0f} days")
        logger.info(f"- Frequency range: {rfm_metrics['frequency'].min():.0f} to {rfm_metrics['frequency'].max():.0f} orders")
        logger.info(f"- Monetary range: {rfm_metrics['monetary'].min():.2f} to {rfm_metrics['monetary'].max():.2f}")
        
        return rfm_metrics
    
    def _calculate_quintile_scores(self, rfm_data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate quintile scores (1-5) for each RFM dimension.
        
        Scoring logic:
        - Recency: 5 = most recent (lowest days), 1 = least recent (highest days)
        - Frequency: 5 = highest frequency, 1 = lowest frequency  
        - Monetary: 5 = highest value, 1 = lowest value
        """
        rfm_scores = rfm_data.copy()
        
        # Calculate quintiles for each metric
        # Recency: Lower days = higher score (reverse ranking)
        rfm_scores['r_score'] = pd.qcut(
            rfm_scores['recency'].rank(method='first'), 
            q=5, 
            labels=[5, 4, 3, 2, 1]  # Reverse order for recency
        ).astype(int)
        
        # Frequency: Higher count = higher score
        rfm_scores['f_score'] = pd.qcut(
            rfm_scores['frequency'].rank(method='first'), 
            q=5, 
            labels=[1, 2, 3, 4, 5]
        ).astype(int)
        
        # Monetary: Higher value = higher score
        rfm_scores['m_score'] = pd.qcut(
            rfm_scores['monetary'].rank(method='first'), 
            q=5, 
            labels=[1, 2, 3, 4, 5]
        ).astype(int)
        
        # Create combined RFM score string
        rfm_scores['rfm_score'] = (
            rfm_scores['r_score'].astype(str) + 
            rfm_scores['f_score'].astype(str) + 
            rfm_scores['m_score'].astype(str)
        )
        
        # Log score distributions
        logger.info(f"RFM score distributions:")
        logger.info(f"- R scores: {rfm_scores['r_score'].value_counts().sort_index().to_dict()}")
        logger.info(f"- F scores: {rfm_scores['f_score'].value_counts().sort_index().to_dict()}")
        logger.info(f"- M scores: {rfm_scores['m_score'].value_counts().sort_index().to_dict()}")
        
        return rfm_scores
    
    def _assign_segments(self, rfm_scores: pd.DataFrame) -> pd.DataFrame:
        """Assign customer segments based on RFM scores."""
        rfm_segments = rfm_scores.copy()
        
        # Define segment assignment rules based on RFM score combinations
        def assign_segment(row):
            r, f, m = row['r_score'], row['f_score'], row['m_score']
            
            # Champions: High value across all dimensions
            if r >= 4 and f >= 4 and m >= 4:
                return "Champions"
            
            # Loyal Customers: Good recency and high frequency
            elif r >= 3 and f >= 4 and m >= 3:
                return "Loyal Customers"
            
            # Potential Loyalists: Recent customers with growth potential
            elif r >= 4 and f >= 2 and m >= 3:
                return "Potential Loyalists"
            
            # New Customers: Recent but low frequency/monetary
            elif r >= 4 and f <= 2 and m <= 2:
                return "New Customers"
            
            # Promising: Recent buyers with low frequency and monetary
            elif r >= 3 and f <= 2 and m <= 2:
                return "Promising"
            
            # Need Attention: Good frequency but low monetary
            elif r >= 3 and f >= 3 and m <= 2:
                return "Need Attention"
            
            # About to Sleep: Below average recency
            elif r <= 2 and f >= 2 and m >= 2:
                return "About to Sleep"
            
            # At Risk: High value but poor recency
            elif r <= 2 and f >= 3 and m >= 3:
                return "At Risk"
            
            # Cannot Lose Them: High value and frequency but at risk
            elif r <= 2 and f >= 4 and m >= 4:
                return "Cannot Lose Them"
            
            # Hibernating: Low recency and frequency but some value
            elif r <= 2 and f <= 2 and m >= 2:
                return "Hibernating"
            
            # Lost: Poor across all dimensions
            else:
                return "Lost"
        
        rfm_segments['segment'] = rfm_segments.apply(assign_segment, axis=1)
        
        # Log segment distribution
        segment_counts = rfm_segments['segment'].value_counts()
        logger.info(f"Customer segment distribution:")
        for segment, count in segment_counts.items():
            percentage = (count / len(rfm_segments)) * 100
            logger.info(f"- {segment}: {count} customers ({percentage:.1f}%)")
        
        return rfm_segments
    
    def _add_segment_metadata(self, rfm_segments: pd.DataFrame) -> pd.DataFrame:
        """Add segment descriptions and metadata."""
        rfm_final = rfm_segments.copy()
        
        # Add segment descriptions and colors
        rfm_final['segment_description'] = rfm_final['segment'].map(
            lambda x: self.segments.get(x, {}).get('description_en', '')
        )
        
        rfm_final['segment_color'] = rfm_final['segment'].map(
            lambda x: self.segments.get(x, {}).get('color', '#808080')
        )
        
        # Calculate customer lifetime value (revenue-only)
        rfm_final['customer_ltv'] = rfm_final['monetary']  # In this context, LTV = total spent
        
        # Add percentile ranks for better interpretation
        rfm_final['recency_percentile'] = rfm_final['recency'].rank(pct=True, ascending=False) * 100
        rfm_final['frequency_percentile'] = rfm_final['frequency'].rank(pct=True) * 100
        rfm_final['monetary_percentile'] = rfm_final['monetary'].rank(pct=True) * 100
        
        return rfm_final
    
    def get_segment_summary(self, rfm_df: pd.DataFrame) -> Dict[str, Any]:
        """Get summary statistics for each customer segment."""
        if len(rfm_df) == 0:
            return {}
        
        summary = {}
        
        for segment in rfm_df['segment'].unique():
            segment_data = rfm_df[rfm_df['segment'] == segment]
            
            segment_stats = {
                'customer_count': len(segment_data),
                'percentage_of_customers': (len(segment_data) / len(rfm_df)) * 100,
                'total_revenue': float(segment_data['monetary'].sum()),
                'avg_revenue_per_customer': float(segment_data['monetary'].mean()),
                'percentage_of_revenue': (segment_data['monetary'].sum() / rfm_df['monetary'].sum()) * 100,
                'avg_recency_days': float(segment_data['recency'].mean()),
                'avg_frequency': float(segment_data['frequency'].mean()),
                'avg_monetary': float(segment_data['monetary'].mean()),
                'avg_customer_ltv': float(segment_data['customer_ltv'].mean()),
                'rfm_scores': {
                    'avg_r_score': float(segment_data['r_score'].mean()),
                    'avg_f_score': float(segment_data['f_score'].mean()),
                    'avg_m_score': float(segment_data['m_score'].mean())
                }
            }
            
            # Add segment metadata
            if segment in self.segments:
                segment_stats['description'] = self.segments[segment].get('description_en', '')
                segment_stats['color'] = self.segments[segment].get('color', '#808080')
                segment_stats['criteria'] = self.segments[segment].get('criteria', '')
            
            summary[segment] = segment_stats
        
        return summary
    
    def get_rfm_heatmap_data(self, rfm_df: pd.DataFrame) -> Dict[str, Any]:
        """Prepare data for RFM heatmap visualization."""
        if len(rfm_df) == 0:
            return {}
        
        # Create pivot table for heatmap
        heatmap_data = rfm_df.pivot_table(
            values='customer_ltv',
            index='f_score',
            columns='r_score',
            aggfunc='mean',
            fill_value=0
        )
        
        # Count of customers in each cell
        count_data = rfm_df.pivot_table(
            values='customer_ltv',
            index='f_score', 
            columns='r_score',
            aggfunc='count',
            fill_value=0
        )
        
        return {
            'value_heatmap': heatmap_data.to_dict(),
            'count_heatmap': count_data.to_dict(),
            'value_matrix': heatmap_data.values.tolist(),
            'count_matrix': count_data.values.tolist(),
            'r_labels': list(heatmap_data.columns),
            'f_labels': list(heatmap_data.index)
        }
    
    def get_segment_actions(self, segment: str, language: str = 'en') -> List[str]:
        """Get recommended actions for a customer segment."""
        if segment not in self.segments:
            return []
        
        # For now, return English actions (Arabic would be in segments config)
        segment_config = self.segments[segment]
        
        if language == 'ar':
            # Return Arabic actions when available
            actions = segment_config.get('actions_ar', segment_config.get('actions', []))
            return actions if isinstance(actions, list) else []
        else:
            actions = segment_config.get('actions', [])
            return actions if isinstance(actions, list) else []

def perform_rfm_analysis(
    df: pd.DataFrame, 
    analysis_date: Optional[datetime] = None
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Convenience function to perform complete RFM analysis.
    
    Args:
        df: DataFrame with order data
        analysis_date: Analysis date for recency calculation
        
    Returns:
        Tuple of (RFM DataFrame, segment summary)
    """
    analyzer = RFMAnalyzer()
    rfm_scores = analyzer.calculate_rfm_scores(df, analysis_date)
    
    if len(rfm_scores) == 0:
        return rfm_scores, {}
    
    segment_summary = analyzer.get_segment_summary(rfm_scores)
    
    return rfm_scores, segment_summary