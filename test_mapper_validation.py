"""Test mapper validation with Germany data."""

import sys
sys.path.insert(0, r'd:\Advanced Analysis for Salla')

import pandas as pd
from app.ingestion.mapper import ColumnMapper

print("Loading Germany e-commerce data (first 1000 rows)...")
df = pd.read_excel(r'c:\Users\omarr\Downloads\Germany e-commerce data.xlsx\Germany e-commerce data.xlsx', nrows=1000)

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
    print(f"  {canonical:20} <- {source:20} ({confidence:.0%})")
print()

# Validate mappings
print("Validating mappings...")
validation = mapper.validate_mappings(df, detected_mappings)

print(f"Is Valid: {validation['is_valid']}")
print()

if validation['errors']:
    print("❌ Errors:")
    for error in validation['errors']:
        print(f"  • {error}")
    print()

if validation['warnings']:
    print("⚠️ Warnings:")
    for warning in validation['warnings']:
        print(f"  • {warning}")
    print()

if validation['missing_required']:
    print(f"Missing Required: {validation['missing_required']}")
    print()

print(f"Data Quality Score: {validation['data_quality_score']:.1%}")
print()

if validation['is_valid']:
    print("✅ Validation PASSED - Mappings are valid!")
else:
    print("❌ Validation FAILED - Fix errors above")
