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
    
    # Sidebar navigation
    st.sidebar.title(t['app']['title'])
    st.sidebar.markdown(f"*{t['app']['subtitle']}*")
    st.sidebar.markdown("---")
    
    # Language selector
    language_options = {
        'en': 'English 🇬🇧',
        'ar': 'العربية 🇸🇦'
    }
    
    selected_lang = st.sidebar.selectbox(
        "Language / اللغة",
        options=list(language_options.keys()),
        format_func=lambda x: language_options[x],
        index=list(language_options.keys()).index(st.session_state.language),
        key='lang_selector'
    )
    
    if selected_lang != st.session_state.language:
        if selected_lang:
            set_language(selected_lang)
        st.rerun()
    
    # Navigation menu
    st.sidebar.markdown("### " + ("Navigation" if st.session_state.language == 'en' else "التنقل"))
    
    pages = {
        "upload": t['navigation']['upload'],
        "summary": t['navigation']['summary'],
        "insights": t['navigation'].get('insights', 'Financial Insights'),
        "customers": t['navigation']['customers'],
        "cohorts": t['navigation']['cohorts'],
        "products": t['navigation']['products'],
        "actions": t['navigation']['actions']
    }
    
    # Always show navigation, but show a warning if no data is loaded
    if not st.session_state.data_loaded:
        st.sidebar.warning("⚠️ Upload data first" if st.session_state.language == 'en' 
                          else "⚠️ الرجاء رفع البيانات أولاً")
    
    # Navigation radio buttons (always visible)
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
    elif page == "actions":
        from app.ui.pages.actions import render_actions_page
        render_actions_page()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f"<div style='text-align: center; color: #666; font-size: 0.8em;'>{t['app']['version']}</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        st.error(f"An error occurred: {str(e)}")
        st.info("Please check the logs for more details.")