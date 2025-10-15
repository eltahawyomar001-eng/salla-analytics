"""Debug script to analyze E Commerce Dashboard file structure."""
import pandas as pd
import sys

file_path = r'c:\Users\omarr\Downloads\E Commerce Dashboard.xlsx'

print("=" * 80)
print("E COMMERCE DASHBOARD FILE ANALYSIS")
print("=" * 80)

try:
    # Read first 10 rows
    df = pd.read_excel(file_path, nrows=10)
    
    print(f"\n📊 FILE INFO:")
    print(f"   Rows (sample): {len(df)}")
    print(f"   Columns: {len(df.columns)}")
    
    print(f"\n📋 COLUMN NAMES:")
    for i, col in enumerate(df.columns, 1):
        print(f"   {i:2d}. {col}")
    
    print(f"\n🔍 SAMPLE DATA (First 3 Rows):")
    print(df.head(3).to_string())
    
    print(f"\n📈 COLUMN TYPES:")
    for col in df.columns:
        print(f"   {col:30s} -> {df[col].dtype}")
    
    print(f"\n❓ MISSING REQUIRED COLUMNS CHECK:")
    required = ['order_date', 'customer_id', 'order_total']
    
    # Check exact matches (case-sensitive)
    print(f"\n   Checking for exact matches (case-sensitive):")
    for req in required:
        if req in df.columns:
            print(f"   ✅ '{req}' found")
        else:
            print(f"   ❌ '{req}' NOT found")
    
    # Check case-insensitive matches
    print(f"\n   Checking for case-insensitive matches:")
    df_lower = {col.lower(): col for col in df.columns}
    for req in required:
        if req.lower() in df_lower:
            print(f"   ✅ '{req}' found as '{df_lower[req.lower()]}'")
        else:
            print(f"   ❌ '{req}' NOT found (even case-insensitive)")
    
    # Look for likely candidates
    print(f"\n   🔎 Potential column matches:")
    date_cols = [col for col in df.columns if 'date' in col.lower()]
    customer_cols = [col for col in df.columns if 'customer' in col.lower() or 'user' in col.lower() or 'id' in col.lower()]
    total_cols = [col for col in df.columns if 'total' in col.lower() or 'sales' in col.lower() or 'revenue' in col.lower() or 'amount' in col.lower()]
    
    print(f"      Date columns: {date_cols}")
    print(f"      Customer columns: {customer_cols}")
    print(f"      Total/Sales columns: {total_cols}")
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
