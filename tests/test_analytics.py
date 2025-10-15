"""Test suite for Advanced Analysis for Salla."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import RFM_SEGMENTS, CANONICAL_FIELDS
from app.ingestion.reader import XLSXReader
from app.ingestion.mapper import ColumnMapper
from app.ingestion.validators import DataValidator
from app.analytics.kpis import KPICalculator
from app.analytics.rfm import RFMAnalyzer
from app.analytics.cohorts import CohortAnalyzer
from app.analytics.products import ProductAnalyzer
from app.analytics.anomalies import AnomalyDetector


@pytest.fixture
def sample_data():
    """Create sample order data for testing."""
    np.random.seed(42)
    
    num_orders = 100
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    dates = pd.date_range(start=start_date, end=end_date, periods=num_orders)
    
    data = {
        'order_id': [f'ORD{i:04d}' for i in range(num_orders)],
        'order_date': dates,
        'customer_id': np.random.choice([f'CUST{i}' for i in range(1, 21)], num_orders),
        'order_total': np.random.uniform(50, 1000, num_orders),
        'product_name': np.random.choice(['Product A', 'Product B', 'Product C'], num_orders),
        'quantity': np.random.randint(1, 5, num_orders),
        'order_status': np.random.choice(['completed', 'completed', 'completed', 'pending'], num_orders)
    }
    
    return pd.DataFrame(data)


class TestConfiguration:
    """Test configuration settings."""
    
    def test_rfm_segments_defined(self):
        """Test that all RFM segments are properly defined."""
        assert len(RFM_SEGMENTS) == 11
        assert 'Champions' in RFM_SEGMENTS
        assert 'Lost' in RFM_SEGMENTS
        
    def test_canonical_fields_defined(self):
        """Test that canonical fields are defined."""
        assert 'order_id' in CANONICAL_FIELDS
        assert 'order_date' in CANONICAL_FIELDS
        assert 'customer_id' in CANONICAL_FIELDS
        assert 'order_total' in CANONICAL_FIELDS


class TestDataIngestion:
    """Test data ingestion components."""
    
    def test_xlsx_reader_initialization(self):
        """Test XLSXReader initialization."""
        reader = XLSXReader()
        assert reader is not None
        
    def test_arabic_digit_normalization(self):
        """Test Arabic digit conversion."""
        reader = XLSXReader()
        
        # Test Arabic digits
        result = reader.normalize_arabic_digits("١٢٣٤٥٦٧٨٩٠")
        assert result == "1234567890"
        
        # Test mixed content
        result = reader.normalize_arabic_digits("Order ١٢٣")
        assert result == "Order 123"
        
    def test_column_mapper_initialization(self):
        """Test ColumnMapper initialization."""
        mapper = ColumnMapper()
        assert mapper is not None
        
    def test_data_validator_initialization(self):
        """Test DataValidator initialization."""
        validator = DataValidator()
        assert validator is not None


class TestAnalytics:
    """Test analytics components."""
    
    def test_kpi_calculator(self, sample_data):
        """Test KPI calculations."""
        calc = KPICalculator()
        kpis = calc.calculate_all_kpis(sample_data)
        
        assert 'revenue_metrics' in kpis
        assert 'customer_metrics' in kpis
        assert 'order_metrics' in kpis
        
        # Check revenue metrics
        revenue_metrics = kpis['revenue_metrics']
        assert 'total_revenue' in revenue_metrics
        assert revenue_metrics['total_revenue'] > 0
        
    def test_rfm_analyzer(self, sample_data):
        """Test RFM analysis."""
        analyzer = RFMAnalyzer()
        results = analyzer.calculate_rfm_scores(sample_data)
        
        assert 'rfm_dataframe' in results
        assert 'segment_summary' in results
        
        # Check RFM scores are in valid range
        rfm_df = results['rfm_dataframe']
        assert rfm_df['recency_score'].between(1, 5).all()
        assert rfm_df['frequency_score'].between(1, 5).all()
        assert rfm_df['monetary_score'].between(1, 5).all()
        
    def test_cohort_analyzer(self, sample_data):
        """Test cohort analysis."""
        analyzer = CohortAnalyzer()
        results = analyzer.perform_cohort_analysis(sample_data)
        
        assert 'retention_matrix' in results
        assert 'cohort_metrics' in results
        
    def test_product_analyzer(self, sample_data):
        """Test product analysis."""
        analyzer = ProductAnalyzer()
        results = analyzer.analyze_products(sample_data)
        
        assert 'product_performance' in results
        assert 'top_products_by_revenue' in results
        
    def test_anomaly_detector(self, sample_data):
        """Test anomaly detection."""
        detector = AnomalyDetector()
        results = detector.detect_anomalies(sample_data)
        
        assert 'daily_anomalies' in results
        assert 'all_anomalies' in results


class TestRFMScoring:
    """Test RFM scoring logic."""
    
    def test_rfm_segment_assignment(self):
        """Test that RFM scores map to correct segments."""
        # Note: Segment assignment happens internally via _assign_segments
        # which uses a nested function. Testing via full RFM calculation instead.
        analyzer = RFMAnalyzer()
        
        # Create test data with clear segment characteristics
        test_data = pd.DataFrame({
            'customer_id': ['C1', 'C2'],
            'order_id': ['O1', 'O2'],
            'order_date': [pd.Timestamp('2025-01-01'), pd.Timestamp('2023-01-01')],
            'order_total': [1000, 10]
        })
        
        results = analyzer.calculate_rfm_scores(test_data)
        assert 'segment' in results['rfm_scores'].columns
        
    def test_quintile_scoring(self):
        """Test quintile-based scoring."""
        analyzer = RFMAnalyzer()
        
        # Create test data with known distribution
        values = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        scores = pd.qcut(values, q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')
        
        assert len(scores.unique()) <= 5
        assert scores.min() >= 1
        assert scores.max() <= 5


class TestDataValidation:
    """Test data validation logic."""
    
    def test_required_fields_validation(self, sample_data):
        """Test that required fields are validated."""
        validator = DataValidator()
        
        mappings = {
            'order_id': 'order_id',
            'order_date': 'order_date',
            'customer_id': 'customer_id',
            'order_total': 'order_total'
        }
        
        results = validator.validate_dataframe(sample_data, mappings)
        
        assert 'is_valid' in results
        assert 'errors' in results
        assert 'data_quality' in results
        
    def test_data_cleaning(self, sample_data):
        """Test data cleaning functionality."""
        validator = DataValidator()
        
        mappings = {
            'order_id': 'order_id',
            'order_date': 'order_date',
            'customer_id': 'customer_id',
            'order_total': 'order_total'
        }
        
        # Add some duplicate orders
        df_with_dupes = pd.concat([sample_data, sample_data.head(5)])
        
        df_clean, summary = validator.clean_dataframe(df_with_dupes, mappings)
        
        assert len(df_clean) < len(df_with_dupes)
        assert summary['removed_rows'] > 0


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_dataframe(self):
        """Test handling of empty dataframe."""
        df = pd.DataFrame()
        calc = KPICalculator()
        
        with pytest.raises(Exception):
            calc.calculate_all_kpis(df)
            
    def test_single_customer(self):
        """Test RFM with single customer."""
        data = {
            'order_id': ['ORD001', 'ORD002'],
            'order_date': [datetime.now() - timedelta(days=10), datetime.now()],
            'customer_id': ['CUST001', 'CUST001'],
            'order_total': [100, 200]
        }
        df = pd.DataFrame(data)
        
        analyzer = RFMAnalyzer()
        results = analyzer.calculate_rfm_scores(df)
        
        assert results['rfm_dataframe'] is not None
        assert len(results['rfm_dataframe']) == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])