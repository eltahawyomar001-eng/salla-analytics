"""Main Streamlit application for Advanced Analysis for Salla."""

import streamlit as st
import logging
from pathlib import Path
import sys
import warnings

# Suppress specific warnings
warnings.filterwarnings('ignore', message='Using slow pure-python SequenceMatcher')
warnings.filterwarnings('ignore', message='Polars not found')
warnings.filterwarnings('ignore', message='.*xlsx2csv.*')
warnings.filterwarnings('ignore', category=FutureWarning, module='plotly')
warnings.filterwarnings('ignore', message='.*get_group.*')

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import PAGE_CONFIG, DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES
from app.ui.components import setup_page, get_translator, set_language
from app.utils.mobile import inject_screen_detector, is_mobile, show_mobile_tip

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Configure Streamlit page
st.set_page_config(
    page_title=PAGE_CONFIG["page_title"],
    page_icon=PAGE_CONFIG["page_icon"],
    layout="wide",  # type: ignore
    initial_sidebar_state="expanded"  # type: ignore
)

# Initialize session state
if 'language' not in st.session_state:
    st.session_state.language = DEFAULT_LANGUAGE

if 'rtl' not in st.session_state:
    st.session_state.rtl = DEFAULT_LANGUAGE == 'ar'

if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

if 'df_clean' not in st.session_state:
    st.session_state.df_clean = None

if 'mappings' not in st.session_state:
    st.session_state.mappings = {}

if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}

if 'welcome_seen' not in st.session_state:
    st.session_state.welcome_seen = False

# Inject mobile detection (do this early)
inject_screen_detector()

def main():
    """Main application entry point."""
    # Show mobile tip if on mobile device
    if is_mobile():
        show_mobile_tip()
    
    # Setup page with language selector
    setup_page()
    
    # Get translator for current language
    t = get_translator(st.session_state.language)
    
    # Modern Sidebar with NEW Gradient Header (Using Theme System)
    st.sidebar.markdown("""
    <div style='background: linear-gradient(135deg, #7C3AED 0%, #2563EB 100%); 
                padding: 1.75rem; 
                border-radius: var(--radius-xl, 16px); 
                margin-bottom: 1.5rem;
                text-align: center;
                box-shadow: var(--shadow-lg, 0 10px 15px -3px rgba(0, 0, 0, 0.1));'>
        <div style='font-size: 2.5rem; margin-bottom: 0.5rem;'>🧠</div>
        <h2 style='color: white; margin: 0; font-size: 1.5rem; font-weight: 700;'>
            """ + t['app']['title'] + """
        </h2>
        <p style='color: rgba(255,255,255,0.95); margin: 0.5rem 0 0 0; font-size: 0.9rem; font-weight: 500;'>
            """ + t['app']['subtitle'] + """
        </p>
        <div style='background: rgba(255,255,255,0.25); 
                    padding: 0.375rem 1rem; 
                    border-radius: 20px; 
                    display: inline-block;
                    margin-top: 1rem;
                    font-size: 0.75rem;
                    color: white;
                    font-weight: 600;
                    letter-spacing: 0.5px;'>
            v2.0.0 🆕
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Language selector - Modern Toggle
    st.sidebar.markdown("### 🌍 " + ("Language" if st.session_state.language == 'en' else "اللغة"))
    
    # Create language toggle buttons with modern styling
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🇬🇧 EN", 
                    use_container_width=True, 
                    type="primary" if st.session_state.language == 'en' else "secondary",
                    help="Switch to English"):
            set_language('en')
            st.rerun()
    with col2:
        if st.button("🇸🇦 عربي", 
                    use_container_width=True,
                    type="primary" if st.session_state.language == 'ar' else "secondary",
                    help="التبديل إلى العربية"):
            set_language('ar')
            st.rerun()
    
    st.sidebar.markdown("---")
    
    # Data Status Indicator - NEW MODERN DESIGN
    if not st.session_state.data_loaded:
        st.sidebar.markdown("""
        <div style='background: linear-gradient(135deg, #F59E0B 0%, #EF4444 100%); 
                    padding: 1.125rem; 
                    border-radius: var(--radius-lg, 12px);
                    margin-bottom: 1.25rem;
                    text-align: center;
                    box-shadow: var(--shadow-md, 0 4px 6px -1px rgba(0, 0, 0, 0.1));
                    border: 2px solid rgba(255,255,255,0.2);'>
            <div style='font-size: 1.75rem; margin-bottom: 0.25rem;'>📤</div>
            <p style='color: white; margin: 0; font-weight: 600; font-size: 0.95rem; letter-spacing: 0.3px;'>
                """ + ("Start by uploading your data" if st.session_state.language == 'en' 
                          else "ابدأ برفع البيانات") + """
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown("""
        <div style='background: linear-gradient(135deg, #10B981 0%, #059669 100%); 
                    padding: 1.125rem; 
                    border-radius: var(--radius-lg, 12px);
                    margin-bottom: 1.25rem;
                    text-align: center;
                    box-shadow: var(--shadow-md, 0 4px 6px -1px rgba(0, 0, 0, 0.1));
                    border: 2px solid rgba(255,255,255,0.2);'>
            <div style='font-size: 1.75rem; margin-bottom: 0.25rem;'>✅</div>
            <p style='color: white; margin: 0; font-weight: 600; font-size: 0.95rem; letter-spacing: 0.3px;'>
                """ + ("Data Ready - Explore Analytics" if st.session_state.language == 'en' 
                          else "البيانات جاهزة - استكشف التحليلات") + """
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Navigation menu with modern styling
    st.sidebar.markdown("<h3 style='margin-bottom: 0.5rem;'>📍 " + 
                       ("Navigation" if st.session_state.language == 'en' else "التنقل") + 
                       "</h3>", unsafe_allow_html=True)
    
    # Enhanced navigation with priority indicators
    if st.session_state.language == 'en':
        pages = {
            "upload": "📤 Upload & Map Data",
            "salla_import": "🔌 Salla Import 🆕",
            "summary": "📊 Executive Summary ⭐",
            "insights": "💰 Financial Insights ⭐",
            "customers": "👥 Customer Segments",
            "cohorts": "📈 Cohort Analysis",
            "products": "🛍️ Product Performance",
            "geo_analytics": "🗺️ Geographic Analytics 🆕",
            "actions": "⚡ Action Playbooks ⭐"
        }
    else:
        pages = {
            "upload": "📤 رفع وربط البيانات",
            "salla_import": "🔌 استيراد سلة 🆕",
            "summary": "📊 الملخص التنفيذي ⭐",
            "insights": "💰 الرؤى المالية ⭐",
            "customers": "👥 شرائح العملاء",
            "cohorts": "📈 تحليل المجموعات",
            "products": "🛍️ أداء المنتجات",
            "geo_analytics": "🗺️ التحليلات الجغرافية 🆕",
            "actions": "⚡ خطط العمل ⭐"
        }
    
    # Navigation radio buttons with custom styling
    page = st.sidebar.radio(
        "Go to" if st.session_state.language == 'en' else "انتقل إلى",
        options=list(pages.keys()),
        format_func=lambda x: pages[x],
        label_visibility="collapsed",
        key="page_selector"
    )
    
    # Load the selected page
    if page == "upload":
        from app.ui.pages.upload import render_upload_page
        render_upload_page()
    elif page == "salla_import":
        from app.ui.pages.salla_import import render_salla_import_page
        render_salla_import_page()
    elif not st.session_state.data_loaded:
        # If user tries to access other pages without data, redirect to upload
        st.warning("⚠️ Please upload and process your data first.")
        from app.ui.pages.upload import render_upload_page
        render_upload_page()
    elif page == "summary":
        from app.ui.pages.summary import render_summary_page
        render_summary_page()
    elif page == "insights":
        from app.ui.pages.insights import render_insights_page
        render_insights_page()
    elif page == "customers":
        from app.ui.pages.customers import render_customers_page
        render_customers_page()
    elif page == "cohorts":
        from app.ui.pages.cohorts import render_cohorts_page
        render_cohorts_page()
    elif page == "products":
        from app.ui.pages.products import render_products_page
        render_products_page()
    elif page == "geo_analytics":
        from app.ui.pages.geo_analytics import render_geo_analytics_page
        render_geo_analytics_page()
    elif page == "actions":
        from app.ui.pages.actions import render_actions_page
        render_actions_page()
    
    # Modern Footer with NEW Gradient
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style='background: linear-gradient(135deg, #7C3AED 0%, #2563EB 100%); 
                padding: 1.25rem; 
                border-radius: var(--radius-lg, 12px);
                margin-top: 1.5rem;
                text-align: center;
                box-shadow: var(--shadow-md, 0 4px 6px -1px rgba(0, 0, 0, 0.1));'>
        <p style='color: white; margin: 0; font-size: 0.8rem; font-weight: 600;'>
            """ + t['app']['version'] + """ - v2.0.0
        </p>
        <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 0.7rem; font-weight: 500;'>
            🗺️ Geographic Analytics Edition
        </p>
        <p style='color: rgba(255,255,255,0.85); margin: 0.5rem 0 0 0; font-size: 0.7rem;'>
            Made with ❤️ for Salla Merchants
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        st.error(f"An error occurred: {str(e)}")
        st.info("Please check the logs for more details.")