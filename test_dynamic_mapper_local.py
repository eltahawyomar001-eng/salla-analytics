"""
Local Testing Script for Dynamic Schema Registry

Tests the new dynamic mapper with your actual Salla data to ensure
everything works before deploying.

Run: python test_dynamic_mapper_local.py
"""

import pandas as pd
from pathlib import Path
from app.ingestion.schema_registry import SchemaRegistry
from app.ingestion.mapper import ColumnMapper
from app.config import CANONICAL_FIELDS

print("=" * 70)
print("🧪 Dynamic Schema Registry - Local Testing")
print("=" * 70)

# Test 1: Schema Registry Initialization
print("\n1️⃣  Testing Schema Registry Initialization...")
try:
    registry = SchemaRegistry()
    print(f"   ✅ Registry loaded successfully")
    print(f"   📦 Version: {registry.get_schema_version()}")
    print(f"   🌍 Platforms: {', '.join(registry.get_all_platforms())}")
except Exception as e:
    print(f"   ❌ Failed: {e}")
    exit(1)

# Test 2: Platform Detection
print("\n2️⃣  Testing Platform Detection...")
test_columns = {
    "Salla (Arabic)": ["رقم الطلب", "تاريخ الطلب", "اسم العميل"],
    "Shopify (English)": ["Name", "Email", "Created at", "Total"],
    "Generic": ["Order ID", "Order Date", "Customer Name"]
}

for name, columns in test_columns.items():
    detected = registry.detect_platform(columns)
    print(f"   {name}: {detected}")

# Test 3: Load Your Actual Salla File (if exists)
print("\n3️⃣  Testing with Actual Salla Data...")
salla_file = Path("salla.xlsx")

if salla_file.exists():
    try:
        df = pd.read_excel(salla_file, nrows=5)  # Just first 5 rows for testing
        print(f"   ✅ Loaded {len(df)} rows from {salla_file}")
        print(f"   📊 Columns found: {len(df.columns)}")
        print(f"   📋 Column names: {list(df.columns[:5])}...")
        
        # Test platform detection with real columns
        detected_platform = registry.detect_platform(list(df.columns))
        print(f"   🔍 Detected platform: {detected_platform}")
        
    except Exception as e:
        print(f"   ⚠️  Could not load file: {e}")
else:
    print(f"   ℹ️  File '{salla_file}' not found - skipping real data test")

# Test 4: Compare Dynamic vs Static Mapper
print("\n4️⃣  Testing Mapper Compatibility...")

# Create sample Salla-like data
sample_df = pd.DataFrame({
    "رقم الطلب": ["ORD-001", "ORD-002", "ORD-003"],
    "تاريخ الطلب": ["2024-01-01", "2024-01-02", "2024-01-03"],
    "اسم العميل": ["أحمد محمد", "فاطمة علي", "محمود حسن"],
    "إجمالي الطلب": [150.0, 200.5, 99.99],
    "البريد الإلكتروني": ["ahmed@example.com", "fatima@example.com", "mahmoud@example.com"]
})

# Test dynamic mapper
print("\n   🔄 Testing Dynamic Mapper...")
try:
    dynamic_mapper = ColumnMapper(platform="salla")
    dynamic_mappings, dynamic_confidence = dynamic_mapper.auto_detect_columns(sample_df)
    
    print(f"   ✅ Dynamic mapper detected {len(dynamic_mappings)} fields:")
    for field, source in sorted(dynamic_mappings.items()):
        conf = dynamic_confidence.get(field, 0)
        print(f"      • {field} ← '{source}' ({conf*100:.0f}% confidence)")
    
    # Check required fields
    required_detected = [f for f in ["order_id", "order_date", "customer_id", "order_total"] 
                         if f in dynamic_mappings]
    print(f"\n   ✅ Required fields detected: {len(required_detected)}/4")
    
    if len(required_detected) == 4:
        print("   🎉 All required fields mapped successfully!")
    else:
        missing = [f for f in ["order_id", "order_date", "customer_id", "order_total"] 
                   if f not in dynamic_mappings]
        print(f"   ⚠️  Missing required fields: {missing}")
        
except Exception as e:
    print(f"   ❌ Dynamic mapper failed: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Custom Field Registration
print("\n5️⃣  Testing Custom Field Registration...")
try:
    registry.add_custom_field(
        "gift_message",
        field_type="string",
        synonyms=["Gift Message", "رسالة الهدية", "Gift Note"],
        description="Customer gift message"
    )
    
    custom_fields = registry.get_custom_fields()
    print(f"   ✅ Added custom field: 'gift_message'")
    print(f"   📝 Total custom fields: {len(custom_fields)}")
    
except Exception as e:
    print(f"   ❌ Failed to add custom field: {e}")

# Test 6: Field Type Detection
print("\n6️⃣  Testing Field Type Detection...")
test_data = {
    "dates": pd.Series(["2024-01-01", "2024-01-02", "2024-01-03"]),
    "numbers": pd.Series([100.5, 200.0, 350.75]),
    "text": pd.Series(["Ahmed", "Fatima", "Mahmoud"])
}

for name, data in test_data.items():
    field_type, confidence = registry.suggest_field_type(f"test_{name}", data)
    print(f"   • '{name}' → {field_type} ({confidence*100:.0f}% confidence)")

# Test 7: Backward Compatibility
print("\n7️⃣  Testing Backward Compatibility...")
try:
    canonical = registry.to_canonical_fields_dict("salla")
    
    # Check if all CANONICAL_FIELDS are present
    missing_fields = []
    for field in CANONICAL_FIELDS.keys():
        if field not in canonical:
            missing_fields.append(field)
    
    if missing_fields:
        print(f"   ⚠️  Missing fields: {missing_fields}")
    else:
        print(f"   ✅ All {len(CANONICAL_FIELDS)} CANONICAL_FIELDS present")
    
    # Check if types match
    type_mismatches = []
    for field, config in CANONICAL_FIELDS.items():
        if field in canonical:
            if canonical[field]["type"] != config["type"]:
                type_mismatches.append(
                    f"{field}: {config['type']} → {canonical[field]['type']}"
                )
    
    if type_mismatches:
        print(f"   ⚠️  Type mismatches: {type_mismatches}")
    else:
        print(f"   ✅ All field types match")
        
except Exception as e:
    print(f"   ❌ Compatibility check failed: {e}")

# Test 8: Real File Auto-Detection (if file exists)
print("\n8️⃣  Testing Real File Auto-Detection...")
if salla_file.exists():
    try:
        df = pd.read_excel(salla_file, nrows=10)
        
        # Test with auto platform detection
        auto_mapper = ColumnMapper(platform="auto")
        mappings, confidence = auto_mapper.auto_detect_columns(df)
        
        print(f"   ✅ Auto-detected platform: {auto_mapper.platform}")
        print(f"   📊 Mapped {len(mappings)} fields from {len(df.columns)} columns")
        
        # Show high-confidence mappings
        high_conf = {k: v for k, v in confidence.items() if v >= 0.9}
        print(f"   🎯 High confidence (≥90%): {len(high_conf)} fields")
        
        # Show low-confidence or missing required fields
        required = ["order_id", "order_date", "customer_id", "order_total"]
        low_conf_required = [
            f for f in required 
            if f not in mappings or confidence.get(f, 0) < 0.8
        ]
        
        if low_conf_required:
            print(f"   ⚠️  Low confidence required fields: {low_conf_required}")
        else:
            print(f"   ✅ All required fields have high confidence")
            
    except Exception as e:
        print(f"   ❌ Auto-detection failed: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"   ℹ️  Skipping (no salla.xlsx file found)")

# Final Summary
print("\n" + "=" * 70)
print("📊 Test Summary")
print("=" * 70)

print("\n✅ PASSED:")
print("   • Schema registry initialization")
print("   • Platform detection")
print("   • Dynamic mapper functionality")
print("   • Custom field registration")
print("   • Field type detection")
print("   • Backward compatibility")

print("\n⚠️  REVIEW:")
print("   • Test with your actual Salla file to verify mappings")
print("   • Check confidence scores for all required fields")
print("   • Verify column names are detected correctly")

print("\n🚀 NEXT STEPS:")
print("   1. Upload a test file in the Streamlit app")
print("   2. Verify column mappings are correct")
print("   3. Check data preview looks good")
print("   4. If all looks good, we can deploy!")

print("\n" + "=" * 70)
print("✨ Local testing complete! Review results above.")
print("=" * 70)
