# Changelog

All notable changes to Salla Advanced Analytics will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-10-16

### 🎉 Major Features Added

#### Geographic Analytics (Feature #9)
- **Multi-language location detection** - Supports English, Arabic, German, French, Spanish, Turkish, Italian
- **8 location types** - City, State, Country, Region, Province, County, Postal Code, Address
- **Intelligent column detection** - Automatically identifies location columns in any e-commerce format
- **Revenue distribution maps** - Interactive choropleth maps and treemaps
- **Location-based insights** - Top cities, revenue concentration, customer distribution
- **Export functionality** - Download geo analytics data as CSV/Excel
- **Robust validation** - Filters out false positives (coupon codes, customer names)
- **Tested with multiple platforms** - Salla, international e-commerce, German shops

### 🐛 Bug Fixes

#### Cohort Analysis
- **Fixed retention matrix display** - Resolved Period serialization error in Plotly heatmaps
- **Dictionary to DataFrame conversion** - Properly handles retention matrix stored in session state
- **Cohort summary metrics** - Added total cohorts, average retention, best performing cohort
- **Improved empty state** - Better messaging when data insufficient for cohort analysis

#### Data Processing
- **Postal code detection** - Fixed false positive matching coupon codes in Arabic files
- **Uniqueness ratio validation** - Prevents address/postal code columns with >80% unique values
- **Type safety improvements** - Fixed all Pylance type errors for production deployment

### ✨ UI/UX Enhancements

#### Modern Design System
- **Gradient hero sections** - Beautiful gradients for better visual hierarchy
- **Improved card designs** - Modern shadows, hover effects, better spacing
- **Action-focused CTAs** - Clear call-to-action buttons throughout
- **Progress indicators** - Better feedback during data processing
- **Responsive layouts** - Optimized for all screen sizes

#### Navigation
- **Clearer menu structure** - Organized navigation with icons
- **Quick access cards** - Jump to any analysis from dashboard
- **Breadcrumb improvements** - Better context awareness

#### Data Upload
- **Enhanced file preview** - See data structure before processing
- **Drag-and-drop improvements** - Better visual feedback
- **Validation messages** - Clearer error messages and suggestions
- **Processing transparency** - Real-time progress updates

#### Dashboard
- **Modern KPI cards** - Redesigned metric cards with trends
- **Better chart layouts** - Optimized spacing and readability
- **Export buttons** - Quick export from any chart
- **Mobile optimization** - Better mobile experience

### 🔧 Technical Improvements

- **Code cleanup** - Removed diagnostic files (analyze_files.py, check_cohort_viability.py, test_postal_fix.py)
- **Type annotations** - Added proper type hints for better IDE support
- **Error handling** - Improved error messages and recovery
- **Performance optimization** - Faster data loading and analysis
- **Logging enhancements** - Better debug information

### 📚 Documentation

- **Added CHANGELOG.md** - Comprehensive version history
- **Improved README** - Updated features list
- **Code comments** - Better inline documentation

---

## [1.0.0] - 2025-10-15

### Initial Release

#### Core Features
- **Data Upload & Validation** - Smart column mapping for Salla exports
- **KPI Dashboard** - Revenue, orders, customers, AOV metrics
- **RFM Customer Segmentation** - 9 customer segments with actionable insights
- **Cohort Analysis** - Monthly cohort retention tracking
- **Product Analytics** - Top products, categories, performance metrics
- **Anomaly Detection** - Automatic identification of unusual patterns
- **Customer Actions** - Targeted recommendations for each segment
- **Multi-language Support** - English and Arabic interfaces
- **Export Functionality** - Download analysis as Excel/CSV

#### Technical Stack
- Streamlit 1.29.0
- Pandas 2.2+
- Plotly 5.18.0
- Python 3.11
- Railway.app deployment
- Nixpacks builder

---

## Version History

- **2.0.0** (Current) - Major UI/UX overhaul + Geographic Analytics + Cohort fixes
- **1.0.0** - Initial release with core analytics features
