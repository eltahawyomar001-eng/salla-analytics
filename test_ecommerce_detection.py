"""Test column detection for E Commerce Dashboard."""

import sys
sys.path.insert(0, r'd:\Advanced Analysis for Salla')

import pandas as pd
from app.ingestion.mapper import ColumnMapper

print("Loading E Commerce Dashboard (first 1000 rows)...")
df = pd.read_excel(r'c:\Users\omarr\Downloads\E Commerce Dashboard.xlsx', nrows=1000)

print(f"✓ Loaded {len(df):,} rows")
print(f"✓ Columns: {list(df.columns)}")
print()

# Create mapper and detect columns
print("Auto-detecting columns...")
mapper = ColumnMapper()
detected_mappings, confidence_scores = mapper.auto_detect_columns(df)

print("Detected mappings:")
for canonical, source in detected_mappings.items():
    confidence = confidence_scores.get(canonical, 0.0)
    print(f"  {canonical:20} <- {source:25} ({confidence:.0%})")
print()

# Check if required fields are mapped
required_fields = ['order_id', 'order_date', 'customer_id', 'order_total']
missing = [f for f in required_fields if f not in detected_mappings]

if missing:
    print(f"❌ Missing required fields: {missing}")
    print()
    print("Available columns that might match:")
    for col in df.columns:
        print(f"  - {col}")
else:
    print("✅ All required fields detected!")

# Validate mappings
print("\nValidating mappings...")
validation = mapper.validate_mappings(df, detected_mappings)

print(f"Is Valid: {validation['is_valid']}")

if validation['errors']:
    print("\n❌ Errors:")
    for error in validation['errors']:
        print(f"  • {error}")

if validation['warnings']:
    print("\n⚠️ Warnings:")
    for warning in validation['warnings']:
        print(f"  • {warning}")
