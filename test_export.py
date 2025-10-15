"""Test script to verify export functionality."""

import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.export.workbook import ExcelReportGenerator
from app.analytics.rfm import RFMAnalyzer
from app.analytics.kpis import calculate_kpis

def test_export():
    """Test export with sample data."""
    print("Loading data...")
    
    # Load the actual Salla data
    data_file = Path("data/salla_export.xlsx")
    if not data_file.exists():
        print(f"Error: {data_file} not found")
        return False
    
    df = pd.read_excel(data_file)
    print(f"Loaded {len(df)} rows")
    
    # Clean data
    df_clean = df.copy()
    
    # Ensure customer_id column exists
    if 'customer_id' not in df_clean.columns:
        if 'رقم العميل' in df_clean.columns:
            df_clean['customer_id'] = df_clean['رقم العميل']
        else:
            print("Error: No customer_id column found")
            return False
    
    # Ensure order_total column exists
    if 'order_total' not in df_clean.columns:
        if 'الإجمالي' in df_clean.columns:
            df_clean['order_total'] = df_clean['الإجمالي']
        else:
            print("Error: No order_total column found")
            return False
    
    # Ensure order_date column exists
    if 'order_date' not in df_clean.columns:
        if 'تاريخ الطلب' in df_clean.columns:
            df_clean['order_date'] = pd.to_datetime(df_clean['تاريخ الطلب'])
        else:
            print("Error: No order_date column found")
            return False
    
    print("Running KPI analysis...")
    kpis = calculate_kpis(df_clean, currency=None)  # Fixed: removed 'language' parameter, added 'currency'
    
    print("Running RFM analysis...")
    rfm_analyzer = RFMAnalyzer()  # Fixed: RFMAnalyzer takes no arguments in __init__
    rfm_df = rfm_analyzer.calculate_rfm_scores(df_clean)  # Fixed: use calculate_rfm_scores method
    rfm_results = {
        'rfm_data': rfm_df,
        'segment_summary': rfm_analyzer.get_segment_summary(rfm_df),
        'heatmap_data': rfm_analyzer.get_rfm_heatmap_data(rfm_df)
    }
    
    print("Creating analysis results...")
    analysis_results = {
        'kpis': kpis,
        'rfm': rfm_results,
        'cohorts': {},
        'products': {},
        'anomalies': {}
    }
    
    print("Generating Excel report...")
    generator = ExcelReportGenerator(language='en')
    
    try:
        excel_buffer = generator.generate_report(
            df_clean=df_clean,
            analysis_results=analysis_results,
            validation_report={'data_quality': {'overall_score': 0.95}},
            translations={}
        )
        
        # Save to file
        output_file = Path("test_export_output.xlsx")
        with open(output_file, 'wb') as f:
            f.write(excel_buffer.getvalue())
        
        print(f"\n✅ SUCCESS! Export saved to: {output_file.absolute()}")
        print(f"File size: {output_file.stat().st_size / 1024:.1f} KB")
        
        # Verify sheets
        test_df = pd.ExcelFile(output_file)
        print(f"\nSheets created: {len(test_df.sheet_names)}")
        for sheet in test_df.sheet_names:
            print(f"  - {sheet}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_export()
    sys.exit(0 if success else 1)
