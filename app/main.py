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

if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

if 'df_clean' not in st.session_state:
    st.session_state.df_clean = None

if 'mappings' not in st.session_state:
    st.session_state.mappings = {}

if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}

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
    
    # Modern Sidebar with Gradient Header
    st.sidebar.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 1.5rem; 
                border-radius: 10px; 
                margin-bottom: 1.5rem;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
        <h2 style='color: white; margin: 0; font-size: 1.5rem;'>
            """ + t['app']['title'] + """
        </h2>
        <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 0.9rem;'>
            """ + t['app']['subtitle'] + """
        </p>
        <div style='background: rgba(255,255,255,0.2); 
                    padding: 0.25rem 0.75rem; 
                    border-radius: 20px; 
                    display: inline-block;
                    margin-top: 0.75rem;
                    font-size: 0.75rem;
                    color: white;
                    font-weight: 500;'>
            v2.0.0 - Geographic Analytics Edition
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
    
    # Data Status Indicator - More Prominent
    if not st.session_state.data_loaded:
        st.sidebar.markdown("""
        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    padding: 1rem; 
                    border-radius: 8px;
                    margin-bottom: 1rem;
                    text-align: center;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
            <p style='color: white; margin: 0; font-weight: 500; font-size: 0.9rem;'>
                💡 """ + ("Start by uploading your data" if st.session_state.language == 'en' 
                          else "ابدأ برفع البيانات") + """
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown("""
        <div style='background: linear-gradient(135deg, #0ba360 0%, #3cba92 100%); 
                    padding: 1rem; 
                    border-radius: 8px;
                    margin-bottom: 1rem;
                    text-align: center;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
            <p style='color: white; margin: 0; font-weight: 500; font-size: 0.9rem;'>
                ✅ """ + ("Data Ready - Explore Analytics" if st.session_state.language == 'en' 
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
    
    # Modern Footer with Gradient
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 1rem; 
                border-radius: 8px;
                margin-top: 1rem;
                text-align: center;'>
        <p style='color: white; margin: 0; font-size: 0.75rem; font-weight: 500;'>
            """ + t['app']['version'] + """ - v2.0.0
        </p>
        <p style='color: rgba(255,255,255,0.8); margin: 0.25rem 0 0 0; font-size: 0.65rem;'>
            🆕 Geographic Analytics Edition
        </p>
        <p style='color: rgba(255,255,255,0.7); margin: 0.5rem 0 0 0; font-size: 0.65rem;'>
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