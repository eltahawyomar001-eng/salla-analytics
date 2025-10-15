"""Test aggregation with Germany e-commerce data."""

import sys
sys.path.insert(0, r'd:\Advanced Analysis for Salla')

import pandas as pd
from app.ingestion.aggregator import DataAggregator
from app.ingestion.mapper import ColumnMapper

print("Loading Germany e-commerce data...")
df = pd.read_excel(r'c:\Users\omarr\Downloads\Germany e-commerce data.xlsx\Germany e-commerce data.xlsx')

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

# Create simple mappings dict
mappings = {
    'customer_id': 'user_id',
    'order_date': 'order_date', 
    'order_total': 'item_price'
}

# Rename columns
df_renamed = df.rename(columns={v: k for k, v in mappings.items()})

print("Detecting data level...")
aggregator = DataAggregator()
detection = aggregator.detect_data_level(df_renamed, mappings)

print(f"Data Level: {detection['data_level']}")
print(f"Confidence: {detection['confidence']:.0%}")
print(f"Indicators: {detection['indicators']}")
print(f"Requires Aggregation: {detection['requires_aggregation']}")
print(f"Strategy: {detection['aggregation_strategy']}")
print()

if detection['requires_aggregation']:
    print("Aggregating to order level...")
    df_orders = aggregator.aggregate_to_orders(df_renamed, mappings)
    
    print(f"✓ Created {len(df_orders):,} orders from {len(df):,} line items")
    print()
    
    summary = aggregator.get_aggregation_summary(df_renamed, df_orders)
    print("Aggregation Summary:")
    for key, value in summary.items():
        if isinstance(value, float):
            print(f"  {key}: {value:,.2f}")
        else:
            print(f"  {key}: {value:,}")
    print()
    
    print("Sample aggregated orders:")
    print(df_orders.head(10))
    print()
    
    print("Columns in aggregated data:")
    print(df_orders.columns.tolist())
    print()
    
    print("Data types:")
    print(df_orders.dtypes)
    
    # Test if it's ready for analysis
    required_cols = ['order_id', 'order_date', 'customer_id', 'order_total']
    has_required = all(col in df_orders.columns for col in required_cols)
    
    print()
    print(f"✓ Has all required columns: {has_required}")
    
    if has_required:
        print("✅ Data is ready for analysis!")
    else:
        missing = [col for col in required_cols if col not in df_orders.columns]
        print(f"❌ Missing columns: {missing}")
else:
    print("No aggregation needed - data is already at order level")
