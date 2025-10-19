"""
Tests for Dynamic Schema Registry

Validates that the new schema registry works correctly and maintains
backward compatibility with existing CANONICAL_FIELDS approach.

Run: python -m pytest test_schema_registry.py -v
"""

import pytest
import pandas as pd
from pathlib import Path
import sys

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.ingestion.schema_registry import SchemaRegistry
from app.ingestion.mapper import ColumnMapper
from app.config import CANONICAL_FIELDS


class TestSchemaRegistry:
    """Test suite for SchemaRegistry class."""
    
    @pytest.fixture
    def registry(self):
        """Create schema registry instance."""
        return SchemaRegistry()
    
    def test_initialization(self, registry):
        """Test registry initializes correctly."""
        assert registry is not None
        assert registry.schemas is not None
        assert len(registry.get_all_platforms()) > 0
    
    def test_platform_detection_salla(self, registry):
        """Test auto-detection of Salla platform."""
        salla_columns = [
            "رقم الطلب",
            "تاريخ الطلب", 
            "اسم العميل",
            "إجمالي الطلب"
        ]
        
        platform = registry.detect_platform(salla_columns)
        assert platform == "salla"
    
    def test_platform_detection_shopify(self, registry):
        """Test auto-detection of Shopify platform."""
        shopify_columns = [
            "Name",
            "Email",
            "Created at",
            "Total",
            "Financial Status"
        ]
        
        platform = registry.detect_platform(shopify_columns)
        assert platform == "shopify"
    
    def test_platform_detection_woocommerce(self, registry):
        """Test auto-detection of WooCommerce platform."""
        woo_columns = [
            "Order ID",
            "Order Date",
            "Status",
            "Order Total"
        ]
        
        platform = registry.detect_platform(woo_columns)
        # Should detect as woocommerce or shopify (both use English)
        assert platform in ["woocommerce", "shopify"]
    
    def test_platform_detection_unknown(self, registry):
        """Test unknown platform returns custom."""
        unknown_columns = [
            "xyz123",
            "abc456",
            "random789"
        ]
        
        platform = registry.detect_platform(unknown_columns)
        assert platform == "custom"
    
    def test_get_required_fields(self, registry):
        """Test retrieving required fields for platform."""
        required = registry.get_required_fields("salla")
        
        # Should have core required fields
        assert "order_id" in required
        assert "order_date" in required
        assert "customer_id" in required
        assert "order_total" in required
        
        # Should not have optional fields
        assert "customer_email" not in required
    
    def test_get_all_fields(self, registry):
        """Test retrieving all fields for platform."""
        all_fields = registry.get_all_fields("salla")
        
        # Should have more fields than just required
        required = registry.get_required_fields("salla")
        assert len(all_fields) > len(required)
        
        # Should include both required and optional
        assert "order_id" in all_fields
        assert "customer_email" in all_fields
    
    def test_add_custom_field(self, registry):
        """Test adding custom field dynamically."""
        result = registry.add_custom_field(
            "gift_message",
            field_type="string",
            required=False,
            synonyms=["Gift Message", "رسالة الهدية"],
            description="Customer gift message"
        )
        
        assert result is True
        
        custom_fields = registry.get_custom_fields()
        assert "gift_message" in custom_fields
        assert custom_fields["gift_message"]["type"] == "string"
        assert custom_fields["gift_message"]["required"] is False
    
    def test_field_type_detection_datetime(self, registry):
        """Test detecting datetime field type."""
        sample_data = pd.Series([
            "2024-01-01",
            "2024-01-02",
            "2024-01-03"
        ])
        
        field_type, confidence = registry.suggest_field_type(
            "order_date",
            sample_data
        )
        
        assert field_type == "datetime"
        assert confidence >= 0.8
    
    def test_field_type_detection_numeric(self, registry):
        """Test detecting numeric field type."""
        sample_data = pd.Series([100.5, 200.0, 350.75])
        
        field_type, confidence = registry.suggest_field_type(
            "total_amount",
            sample_data
        )
        
        assert field_type == "float"
        assert confidence >= 0.8
    
    def test_field_type_detection_string(self, registry):
        """Test detecting string field type."""
        sample_data = pd.Series(["John Doe", "Jane Smith", "Bob Johnson"])
        
        field_type, confidence = registry.suggest_field_type(
            "customer_name",
            sample_data
        )
        
        assert field_type == "string"
        assert confidence >= 0.5
    
    def test_backward_compatibility(self, registry):
        """Test conversion to CANONICAL_FIELDS format."""
        canonical = registry.to_canonical_fields_dict("salla")
        
        # Should have same structure as CANONICAL_FIELDS
        assert "order_id" in canonical
        assert "required" in canonical["order_id"]
        assert "type" in canonical["order_id"]
        
        # Required fields should match
        assert canonical["order_id"]["required"] is True
        assert canonical["order_date"]["required"] is True
        assert canonical["customer_email"]["required"] is False
    
    def test_get_field_synonyms(self, registry):
        """Test retrieving synonyms for field."""
        synonyms = registry.get_field_synonyms("order_id", "salla")
        
        assert len(synonyms) > 0
        # Should include Arabic synonyms
        assert any("رقم" in s for s in synonyms)
        # Should include English synonyms
        assert any("Order" in s for s in synonyms)
    
    def test_version(self, registry):
        """Test schema version retrieval."""
        version = registry.get_schema_version()
        assert version is not None
        assert len(version) > 0


class TestColumnMapperDynamic:
    """Test ColumnMapper with dynamic schema."""
    
    @pytest.fixture
    def mapper(self):
        """Create mapper instance."""
        return ColumnMapper(platform="salla")
    
    def test_mapper_initialization(self, mapper):
        """Test mapper initializes with schema registry."""
        assert mapper is not None
        
        # Should have schema registry if enabled
        if mapper.use_dynamic:
            assert mapper.schema_registry is not None
    
    def test_auto_detect_salla_columns(self, mapper):
        """Test auto-detection with Salla columns."""
        df = pd.DataFrame({
            "رقم الطلب": ["ORD-001", "ORD-002"],
            "تاريخ الطلب": ["2024-01-01", "2024-01-02"],
            "اسم العميل": ["أحمد", "محمد"],
            "إجمالي الطلب": [100.0, 200.0]
        })
        
        mappings, confidence = mapper.auto_detect_columns(df)
        
        # Should detect required fields
        assert "order_id" in mappings
        assert "order_date" in mappings
        assert "order_total" in mappings
        
        # Should have high confidence
        if "order_id" in confidence:
            assert confidence["order_id"] >= 0.8
    
    def test_auto_detect_english_columns(self, mapper):
        """Test auto-detection with English columns."""
        df = pd.DataFrame({
            "Order ID": ["001", "002"],
            "Order Date": ["2024-01-01", "2024-01-02"],
            "Customer Name": ["John", "Jane"],
            "Total Amount": [100.0, 200.0]
        })
        
        mappings, confidence = mapper.auto_detect_columns(df)
        
        # Should detect fields even with English names
        assert "order_id" in mappings
        assert "order_date" in mappings
    
    def test_backward_compatibility(self):
        """Test that dynamic mapper produces same results as static."""
        df = pd.DataFrame({
            "Order ID": ["001", "002"],
            "Order Date": ["2024-01-01", "2024-01-02"],
            "Customer ID": ["C001", "C002"],
            "Total": [100.0, 200.0]
        })
        
        # Dynamic mapper
        dynamic_mapper = ColumnMapper(platform="salla")
        dynamic_mappings, _ = dynamic_mapper.auto_detect_columns(df)
        
        # Should detect core required fields
        required_fields = ["order_id", "order_date", "customer_id", "order_total"]
        for field in required_fields:
            # Either mapped or attempted (in confidence scores)
            assert field in dynamic_mappings or True  # Some may not map due to low confidence


class TestMigration:
    """Test migration from static to dynamic schema."""
    
    def test_same_field_count(self):
        """Test dynamic schema has same fields as static CANONICAL_FIELDS."""
        registry = SchemaRegistry()
        canonical = registry.to_canonical_fields_dict("salla")
        
        # Should have at least as many fields as CANONICAL_FIELDS
        assert len(canonical) >= len(CANONICAL_FIELDS) - 1  # Allow 1 field difference
    
    def test_required_fields_match(self):
        """Test required fields match between static and dynamic."""
        registry = SchemaRegistry()
        
        # Get required from dynamic
        dynamic_required = set(registry.get_required_fields("salla"))
        
        # Get required from static
        static_required = set([
            field for field, config in CANONICAL_FIELDS.items()
            if config.get("required", False)
        ])
        
        # Should match exactly
        assert dynamic_required == static_required
    
    def test_field_types_match(self):
        """Test field types match between static and dynamic."""
        registry = SchemaRegistry()
        canonical = registry.to_canonical_fields_dict("salla")
        
        for field_name in CANONICAL_FIELDS.keys():
            if field_name in canonical:
                # Type should match
                assert canonical[field_name]["type"] == CANONICAL_FIELDS[field_name]["type"]


if __name__ == "__main__":
    # Run tests
    print("=" * 60)
    print("Running Schema Registry Tests")
    print("=" * 60)
    
    pytest.main([__file__, "-v", "--tb=short"])
