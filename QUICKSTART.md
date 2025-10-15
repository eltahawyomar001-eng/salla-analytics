# 🚀 Quick Start Guide - Advanced Analysis for Salla

## ✅ Setup Complete!

All components have been successfully created and configured.

## 📋 What's Included

### Core Application
- ✅ Complete Streamlit web application
- ✅ Data ingestion with auto-column detection
- ✅ 5 analytics modules (KPIs, RFM, Cohorts, Products, Anomalies)
- ✅ Bilingual UI (English/Arabic with RTL)
- ✅ Excel export functionality
- ✅ Interactive dashboards with Plotly

### Sample Data
- ✅ `data/sample_salla_orders.xlsx` (982 orders, 100 customers)
- ✅ Test data generator script

### Testing
- ✅ Pytest test suite (`tests/test_analytics.py`)
- ✅ 25+ test cases covering all modules

### Documentation
- ✅ Comprehensive README.md
- ✅ Inline code documentation
- ✅ Configuration files

## 🎯 Run the Application

### Method 1: Using Streamlit directly
```powershell
cd "D:\Advanced Analysis for Salla"
streamlit run app/main.py
```

### Method 2: Using Make (if available)
```powershell
make run
```

The application will open in your browser at: `http://localhost:8501`

## 📊 Test with Sample Data

1. **Start the application** (see above)

2. **Upload sample data:**
   - Click "Browse files"
   - Select `D:\Advanced Analysis for Salla\data\sample_salla_orders.xlsx`
   - Review auto-detected columns
   - Click "Process Data"

3. **Explore the dashboards:**
   - **Executive Summary**: Key metrics and trends
   - **Customers**: RFM segmentation and customer insights
   - **Cohorts**: Retention analysis
   - **Products**: Top performers and market basket
   - **Actions**: Segment-specific recommendations

4. **Export report:**
   - Go to Executive Summary
   - Click "Download Excel Report"
   - Get comprehensive 9-sheet Excel report

## 🧪 Run Tests

```powershell
cd "D:\Advanced Analysis for Salla"
pytest tests/ -v
```

Or with coverage:
```powershell
pytest tests/ -v --cov=app --cov-report=html
```

## 📁 Project Structure

```
D:\Advanced Analysis for Salla\
├── app/
│   ├── main.py                 # Entry point
│   ├── config.py               # Configuration
│   ├── ingestion/              # Data reading & validation
│   │   ├── reader.py
│   │   ├── mapper.py
│   │   └── validators.py
│   ├── analytics/              # Analysis engines
│   │   ├── kpis.py
│   │   ├── rfm.py
│   │   ├── cohorts.py
│   │   ├── products.py
│   │   ├── anomalies.py
│   │   └── explainers.py
│   ├── export/                 # Excel export
│   │   └── workbook.py
│   ├── ui/                     # Streamlit UI
│   │   ├── components.py
│   │   └── pages/
│   ├── i18n/                   # Translations
│   │   ├── en.json
│   │   └── ar.json
│   └── schemas/                # Data schemas
├── data/
│   ├── sample_salla_orders.xlsx
│   └── generate_sample_data.py
├── tests/
│   └── test_analytics.py
├── requirements.txt
├── pyproject.toml
├── Makefile
└── README.md
```

## 🌐 Language Switching

- Click the language selector in the sidebar
- Choose between:
  - **English 🇬🇧**
  - **العربية 🇸🇦** (with RTL support)

## 📤 Using Your Own Data

### Required Columns
Your Excel file must have these columns (any name/language):
- **Order ID**: Unique identifier
- **Order Date**: When the order was placed
- **Customer ID**: Customer identifier
- **Order Total**: Revenue amount

### Optional Columns
- Order Status
- Product Name
- Category
- Quantity
- Unit Price
- Customer Name/Email/Phone
- Currency

### Column Detection
The app will automatically detect your columns! It supports:
- English headers
- Arabic headers (رقم الطلب, تاريخ الطلب, etc.)
- Fuzzy matching for variations
- Manual adjustment if needed

## 🎨 Features Overview

### 1. Data Upload & Validation
- Drag & drop Excel files
- Auto-detect columns with 80%+ confidence
- Data quality scoring
- Duplicate detection
- Business rule validation
- Arabic digit normalization (٠-٩ → 0-9)

### 2. Executive Summary
- Total revenue, orders, customers
- Average order value (AOV)
- Repeat purchase rate
- Customer lifetime value (LTV)
- Monthly revenue trends
- Customer distribution charts

### 3. RFM Customer Segmentation
11 distinct segments:
- **Champions** (R≥4, F≥4, M≥4)
- **Loyal Customers**
- **Potential Loyalists**
- **New Customers**
- **Promising**
- **Needs Attention**
- **About to Sleep**
- **At Risk**
- **Cannot Lose Them**
- **Hibernating**
- **Lost** (R≤2, F≤2, M≤2)

### 4. Cohort Analysis
- Monthly/quarterly cohorts
- Retention heatmap
- Retention rates (1, 3, 6, 12 periods)
- Time to second purchase

### 5. Product Analytics
- Top products by revenue/orders/customers
- Category performance
- Market basket analysis
- Product associations (support, confidence, lift)

### 6. Anomaly Detection
- Daily revenue anomalies
- Monthly trend anomalies
- Extreme order detection
- Seasonal patterns
- Statistical methods (Z-score, IQR)

### 7. Excel Export
9-sheet comprehensive report:
1. Executive Summary
2. KPIs
3. RFM Customers
4. Segments
5. Cohorts
6. Products
7. Anomalies
8. Data Dictionary
9. Run Log

## ⚙️ Configuration

Edit `app/config.py` to customize:
- RFM segment definitions
- Quality thresholds
- Date formats
- Currency settings
- Language preferences

## 🔧 Troubleshooting

### Port already in use
```powershell
streamlit run app/main.py --server.port 8502
```

### Module import errors
```powershell
pip install -r requirements.txt
```

### Excel export fails
Ensure xlsxwriter is installed:
```powershell
pip install xlsxwriter
```

### Arabic text not displaying correctly
Install RTL support:
```powershell
pip install arabic-reshaper python-bidi
```

## 📊 Performance

- **Small files** (<10K rows): < 5 seconds
- **Medium files** (10K-100K rows): < 30 seconds
- **Large files** (100K-1M rows): < 3 minutes (with polars)

Install polars for better performance:
```powershell
pip install polars
```

## 🔒 Privacy

- 100% local processing
- No external API calls
- No data upload to cloud
- All analysis happens on your machine

## 📝 Next Steps

1. **Test with sample data** (already included)
2. **Upload your own Salla data**
3. **Explore all dashboard pages**
4. **Export comprehensive reports**
5. **Customize RFM segments** (optional)
6. **Add more translations** (optional)

## 🆘 Support

- Check README.md for detailed documentation
- Review inline code comments
- Check logs in Streamlit console
- Verify data format matches requirements

## 🎉 You're Ready!

Everything is set up and ready to use. Start the application and begin analyzing your Salla data!

```powershell
streamlit run app/main.py
```

Happy analyzing! 📊✨