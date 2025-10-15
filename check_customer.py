"""Simple debug script - check for customer_id column."""
import pandas as pd

file_path = r'c:\Users\omarr\Downloads\E Commerce Dashboard.xlsx'
df = pd.read_excel(file_path, nrows=5)

print("All columns:")
for i, col in enumerate(df.columns):
    print(f"  {i}: {col}")

print("\nChecking for customer-related columns:")
for col in df.columns:
    if 'customer' in col.lower() or 'user' in col.lower() or 'client' in col.lower():
        print(f"  FOUND: {col}")
