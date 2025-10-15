"""Configuration module for Advanced Analysis for Salla."""

import os
from typing import Dict, List, Any
from pathlib import Path

# Application Settings
APP_NAME = "Advanced Analysis for Salla"
APP_VERSION = "1.0.0"
DEFAULT_CURRENCY = None  # Currency will be detected from data
DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = ["en", "ar"]

# File Processing
MAX_FILE_SIZE_MB = 500
CHUNK_SIZE_ROWS = 10000
MAX_ROWS_PREVIEW = 5

# Analytics Settings
RFM_QUINTILES = [1, 2, 3, 4, 5]
ANOMALY_THRESHOLD_Z = 2.5
MIN_COHORT_SIZE = 10
MIN_DATA_QUALITY_THRESHOLD = 0.8

# UI Settings
PAGE_CONFIG = {
    "page_title": APP_NAME,
    "page_icon": "📊",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Paths
BASE_DIR = Path(__file__).parent
I18N_DIR = BASE_DIR / "i18n"
SCHEMAS_DIR = BASE_DIR / "schemas"
DATA_DIR = BASE_DIR / "data"

# RFM Segment Definitions
RFM_SEGMENTS = {
    "Champions": {
        "criteria": "R>=4 AND F>=4 AND M>=4",
        "description_en": "Best customers who bought recently, buy often and spend the most",
        "description_ar": "أفضل العملاء الذين اشتروا مؤخراً، يشترون بكثرة وينفقون أكثر",
        "color": "#2E8B57"
    },
    "Loyal Customers": {
        "criteria": "R>=3 AND F>=4 AND M>=3",
        "description_en": "Loyal customers with good recency and high frequency",
        "description_ar": "عملاء مخلصون مع شراء حديث وتكرار عالي",
        "color": "#4169E1"
    },
    "Potential Loyalists": {
        "criteria": "R>=4 AND F>=2 AND M>=3",
        "description_en": "Recent customers with potential to become loyal",
        "description_ar": "عملاء حديثون لديهم إمكانية ليصبحوا مخلصين",
        "color": "#32CD32"
    },
    "New Customers": {
        "criteria": "R>=4 AND F<=2 AND M<=2",
        "description_en": "New customers who bought recently but not frequently",
        "description_ar": "عملاء جدد اشتروا مؤخراً لكن ليس بكثرة",
        "color": "#FFD700"
    },
    "Promising": {
        "criteria": "R>=3 AND F<=2 AND M<=2",
        "description_en": "Recent buyers with low frequency and monetary value",
        "description_ar": "مشترون حديثون بتكرار وقيمة نقدية منخفضة",
        "color": "#FFA500"
    },
    "Need Attention": {
        "criteria": "R>=3 AND F>=3 AND M<=2",
        "description_en": "Good frequency but low monetary value",
        "description_ar": "تكرار جيد لكن قيمة نقدية منخفضة",
        "color": "#FF6347"
    },
    "About to Sleep": {
        "criteria": "R<=2 AND F>=2 AND M>=2",
        "description_en": "Below average recency with good frequency and monetary",
        "description_ar": "شراء أقل من المتوسط مع تكرار وقيمة نقدية جيدة",
        "color": "#FF4500"
    },
    "At Risk": {
        "criteria": "R<=2 AND F>=3 AND M>=3",
        "description_en": "High value customers who haven't purchased recently",
        "description_ar": "عملاء عاليو القيمة لم يشتروا مؤخراً",
        "color": "#DC143C"
    },
    "Cannot Lose Them": {
        "criteria": "R<=2 AND F>=4 AND M>=4",
        "description_en": "High value and frequency customers at risk of churning",
        "description_ar": "عملاء عاليو القيمة والتكرار معرضون لخطر الفقدان",
        "color": "#B22222"
    },
    "Hibernating": {
        "criteria": "R<=2 AND F<=2 AND M>=2",
        "description_en": "Low recency and frequency but still valuable",
        "description_ar": "شراء وتكرار منخفض لكن لا يزالون ذوي قيمة",
        "color": "#8B4513"
    },
    "Lost": {
        "criteria": "R<=2 AND F<=2 AND M<=2",
        "description_en": "Customers who haven't bought recently, infrequently and low value",
        "description_ar": "عملاء لم يشتروا مؤخراً، بتكرار قليل وقيمة منخفضة",
        "color": "#696969"
    }
}

# Canonical Schema Definition
CANONICAL_FIELDS = {
    "order_id": {"required": True, "type": "string"},
    "order_date": {"required": True, "type": "datetime"},
    "order_status": {"required": False, "type": "string"},
    "currency": {"required": False, "type": "string"},
    "order_total": {"required": True, "type": "float"},
    "customer_id": {"required": True, "type": "string"},
    "customer_name": {"required": False, "type": "string"},
    "customer_email": {"required": False, "type": "string"},
    "customer_phone": {"required": False, "type": "string"},
    "line_item_id": {"required": False, "type": "string"},
    "product_id": {"required": False, "type": "string"},
    "product_name": {"required": False, "type": "string"},
    "sku": {"required": False, "type": "string"},
    "quantity": {"required": False, "type": "float"},
    "item_total": {"required": False, "type": "float"},
    "discounts": {"required": False, "type": "float"},
    "shipping": {"required": False, "type": "float"},
    "taxes": {"required": False, "type": "float"},
    "refund_amount": {"required": False, "type": "float"},
    "fulfillment_status": {"required": False, "type": "string"},
    "payment_status": {"required": False, "type": "string"},
}

# Export Configuration
EXPORT_SHEETS = [
    "1_Executive_Summary",
    "2_KPIs",
    "3_RFM_Customers",
    "4_Segments",
    "5_Cohorts",
    "6_Products",
    "7_Actions_EN",
    "8_Actions_AR",
    "9_Data_Dictionary",
    "10_Run_Log"
]

# Quality Thresholds
QUALITY_THRESHOLDS = {
    "sparse_field_threshold": 0.05,  # 5% non-null minimum
    "mapping_confidence_threshold": 0.8,
    "min_orders_for_rfm": 10,
    "min_customers_for_cohort": 5
}

# Currency Configuration
CURRENCY_FORMATTING = {
    "SAR": {"symbol": "ر.س", "decimal_places": 2, "position": "suffix"},
    "USD": {"symbol": "$", "decimal_places": 2, "position": "prefix"},
    "EUR": {"symbol": "€", "decimal_places": 2, "position": "suffix"},
    "default": {"symbol": "", "decimal_places": 2, "position": "suffix"}
}

# Arabic Digit Mapping
ARABIC_TO_ENGLISH_DIGITS = {
    '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
    '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9'
}

# Date Patterns for Auto-Detection
DATE_PATTERNS = [
    "%Y-%m-%d",
    "%Y-%m-%d %H:%M:%S",
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%m/%d/%Y",
    "%Y/%m/%d",
    "%d.%m.%Y",
    "%Y.%m.%d"
]

def get_env_var(key: str, default: Any = None) -> Any:
    """Get environment variable with default fallback."""
    return os.getenv(key, default)

def is_rtl_language(language: str) -> bool:
    """Check if language requires RTL layout."""
    return language == "ar"