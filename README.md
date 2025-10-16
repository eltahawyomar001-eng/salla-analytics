# Advanced Analysis for Salla

📊 **A Local, Offline Analytics Tool for Salla XLSX Exports**

Comprehensive revenue analytics with RFM segmentation, cohort analysis, product insights, geographic analytics, and anomaly detection. Built specifically for Salla merchants who want deep insights into their sales data without external dependencies or cloud services.

## ✨ Features

### 🆕 Version 2.0.0 - Geographic Analytics Edition

- **🗺️ Geographic Analytics**: Multi-language location detection supporting 8 location types (City, State, Country, Region, Province, County, Postal Code, Address) in 7+ languages
- **📤 Smart Data Import**: Auto-detects columns with fuzzy matching, supports Arabic headers
- **📈 Executive Summary**: Key metrics with revenue trends and customer distribution  
- **👥 RFM Customer Segmentation**: 11 distinct segments (Champions, Loyal, At Risk, Lost, etc.)
- **📅 Cohort Analysis**: Track customer retention and repeat purchase patterns with enhanced visualization
- **🛍️ Product Analytics**: Top performers, category analysis, market basket insights
- **⚠️ Anomaly Detection**: Statistical outlier detection for revenue and orders
- **🌍 Bilingual Support**: Full English and Arabic UI with RTL support
- **📊 Excel Export**: Comprehensive reports with 10 sheets of insights
- **🎨 Modern UI/UX**: Beautiful gradient designs, action-focused CTAs, improved navigation
- **🔒 Privacy-First**: 100% local processing, no data leaves your machine

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Windows, macOS, or Linux

### Installation

1. **Clone or download** this repository

2. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```powershell
   streamlit run app/main.py
   ```

4. **Open your browser** to `http://localhost:8501`

### First Use

1. Click "Upload" in the sidebar
2. Select your Salla XLSX export file
3. Review auto-detected column mappings (adjust if needed)
4. Click "Process Data"
5. Navigate through the analysis pages

## 📋 Data Requirements

### Required Columns (will be auto-detected)
- **Order ID**: Unique identifier for each order
- **Order Date**: When the order was placed
- **Customer ID**: Unique identifier for each customer
- **Order Total**: Revenue amount for the order

### Optional Columns (enhance analysis)
- Order Status
- Product Name
- Category
- Quantity
- Unit Price
- Customer Name/Email/Phone
- Currency

### Supported File Format
- **XLSX** (Excel 2007+)
- Max file size: 500 MB
- Handles up to 2M+ rows with automatic chunking

## 🎯 Use Cases

### For Merchants
- Identify top customers and high-value segments
- Understand repeat purchase behavior
- Find products that sell together
- Detect unusual patterns in sales
- Plan targeted marketing campaigns

### For Analysts
- Deep-dive customer lifetime value analysis
- Cohort-based retention tracking
- Statistical anomaly detection
- Product performance benchmarking
- Revenue trend analysis

## 📊 Analysis Modules

### 1. Executive Summary
- Total revenue, orders, customers
- Average order value (AOV)
- New vs returning customer ratio
- Monthly revenue trends
- Customer and revenue distribution

### 2. RFM Segmentation
**11 Customer Segments**:
- **Champions**: R≥4, F≥4, M≥4
- **Loyal Customers**: R≥3, F≥4, M≥3
- **Potential Loyalists**: R≥4, F≥2, M≥2
- **New Customers**: R≥4, F=1, M≥1
- **Promising**: R≥3, F=1, M≥1
- **Needs Attention**: R≥3, F≤3, M≤3
- **About to Sleep**: R≤2, F≥2, M≥2
- **At Risk**: R≤2, F≥3, M≥3
- **Cannot Lose Them**: R≤2, F≥4, M≥4
- **Hibernating**: R≤2, F=1, M≥1
- **Lost**: R≤2, F≤2, M≤2

Each segment includes:
- Customer count and revenue
- Recommended actions (5+ specific tactics)
- Segment characteristics and trends

### 3. Cohort Analysis
- Monthly or quarterly cohort grouping
- Retention matrix heatmap
- Retention rates at periods 1, 3, 6, 12
- Time-to-second-purchase distribution
- Cohort performance comparison

### 4. Product Analytics
- Top products by revenue, orders, customers
- Category performance (if data available)
- Market basket analysis (products bought together)
- Support, confidence, and lift metrics
- Product lifecycle tracking

### 5. Anomaly Detection
- Daily revenue and order anomalies
- Monthly trend anomalies with MoM growth
- Extreme order value detection (p1/p99)
- Seasonal pattern analysis (day-of-week, monthly)
- Statistical methods: Modified Z-score (MAD), IQR

## 🔧 Configuration

### Language Settings
Edit `app/config.py`:
```python
DEFAULT_LANGUAGE = "en"  # or "ar"
SUPPORTED_LANGUAGES = ["en", "ar"]
```

### RFM Thresholds
Customize segment criteria in `app/config.py`:
```python
RFM_SEGMENTS = {
    "Champions": {
        "criteria": "R>=4 AND F>=4 AND M>=4",
        # ...
    }
}
```

### Quality Thresholds
```python
QUALITY_THRESHOLDS = {
    'mapping_confidence_threshold': 0.8,
    'data_quality_min_threshold': 0.7,
    # ...
}
```

## 📁 Project Structure

```
Advanced Analysis for Salla/
├── app/
│   ├── main.py                 # Streamlit entry point
│   ├── config.py               # Configuration and constants
│   ├── ingestion/              # Data reading and validation
│   │   ├── reader.py           # XLSX reading with chunking
│   │   ├── mapper.py           # Column auto-detection
│   │   └── validators.py       # Data validation and cleaning
│   ├── analytics/              # Analysis engines
│   │   ├── kpis.py            # KPI calculations
│   │   ├── rfm.py             # RFM segmentation
│   │   ├── cohorts.py         # Cohort analysis
│   │   ├── products.py        # Product analytics
│   │   ├── anomalies.py       # Anomaly detection
│   │   └── explainers.py      # Business insights
│   ├── export/                 # Excel export
│   │   └── workbook.py        # Multi-sheet report generation
│   ├── ui/                     # Streamlit pages
│   │   ├── components.py      # Shared UI components
│   │   └── pages/             # Page modules
│   │       ├── upload.py
│   │       ├── summary.py
│   │       ├── customers.py
│   │       ├── cohorts.py
│   │       ├── products.py
│   │       └── actions.py
│   ├── i18n/                   # Translations
│   │   ├── en.json
│   │   └── ar.json
│   └── schemas/                # Data schemas
│       ├── canonical_schema.yaml
│       └── header_synonyms.yaml
├── tests/                      # Test suite
├── data/                       # Sample data
├── requirements.txt
├── pyproject.toml
├── Makefile
└── README.md
```

## 🧪 Testing

Run the test suite:
```powershell
pytest tests/ -v --cov=app
```

Run type checking:
```powershell
mypy app/
```

Run linting:
```powershell
ruff check app/
black --check app/
```

## 📤 Exporting Reports

Click "Export to Excel" on any page to generate a comprehensive report:

### Report Sheets
1. **Executive Summary**: Key metrics and trends
2. **KPIs**: All calculated metrics
3. **RFM Customers**: Customer list with RFM scores
4. **Segments**: Segment-level statistics
5. **Cohorts**: Retention matrix and metrics
6. **Products**: Product performance table
7. **Actions (EN)**: Recommended actions in English
8. **Actions (AR)**: Recommended actions in Arabic
9. **Data Dictionary**: Field definitions
10. **Run Log**: Processing metadata

## 🌍 Internationalization

### Adding a New Language

1. Create translation file: `app/i18n/XX.json`
2. Copy structure from `en.json`
3. Translate all values
4. Add language code to `SUPPORTED_LANGUAGES` in `config.py`
5. Add language option to UI language selector

### RTL Support

Arabic text is automatically rendered with RTL support when Arabic is selected. Install optional dependencies for better rendering:
```powershell
pip install arabic-reshaper python-bidi
```

## 🔒 Privacy & Security

- **No External APIs**: All processing happens locally
- **No Data Upload**: Your data never leaves your machine
- **No Tracking**: No analytics or telemetry
- **Open Source**: Full transparency of data processing

## ⚡ Performance

### Optimization Features
- **Chunked Reading**: Handles files with 2M+ rows
- **Optional Polars**: 3-5x faster processing for large files
- **Efficient Algorithms**: Vectorized pandas operations
- **Lazy Loading**: Analyses run only when needed

### Benchmarks
- 10K orders: < 5 seconds
- 100K orders: < 30 seconds
- 1M orders: < 3 minutes (with polars)

## 🐛 Troubleshooting

### "Import polars could not be resolved"
This is expected. Polars is optional for performance. Install with:
```powershell
pip install polars
```

### "Import fuzzywuzzy could not be resolved"
This is expected. Fuzzywuzzy is optional for better fuzzy matching. Install with:
```powershell
pip install fuzzywuzzy python-Levenshtein
```

### Arabic text not displaying correctly
Install RTL support:
```powershell
pip install arabic-reshaper python-bidi
```

### File too large to process
Enable chunked reading (automatic for files >10K rows) or install polars for better performance.

### Column mappings not detected
- Check that column headers match expected patterns
- Review `app/schemas/header_synonyms.yaml` for supported synonyms
- Manually adjust mappings in the UI

## 📝 License

This project is provided as-is for educational and commercial use.

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional segment definitions
- More anomaly detection methods
- Enhanced visualizations
- Additional language translations
- Performance optimizations

## 📞 Support

For issues or questions:
1. Check this README and inline code documentation
2. Review `app/i18n/en.json` for error messages
3. Check logs in the Streamlit console
4. Verify data format matches requirements

## 🎯 Roadmap

### ✅ Completed in v2.0.0
- [x] Geographic analysis with multi-language support
- [x] Modern UI/UX with gradient designs
- [x] Enhanced cohort visualization
- [x] Type-safe error handling

### 🚀 Future Enhancements
- [ ] PDF report generation
- [ ] Custom segment builder UI
- [ ] Advanced market basket analysis
- [ ] Forecasting module
- [ ] Customer journey mapping
- [ ] API mode for automation
- [ ] Multi-currency conversion
- [ ] Real-time data refresh capabilities

## 🙏 Acknowledgments

Built with:
- [Streamlit](https://streamlit.io/) - UI framework
- [Pandas](https://pandas.pydata.org/) - Data processing
- [Plotly](https://plotly.com/) - Interactive charts
- [scikit-learn](https://scikit-learn.org/) - Statistical methods

---

**Version 2.0.0** - Made with ❤️ by Omar Rageh for Salla merchants