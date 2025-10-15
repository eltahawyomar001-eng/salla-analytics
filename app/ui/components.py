"""Shared UI components for the Streamlit application."""

import streamlit as st
import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# RTL support
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    RTL_AVAILABLE = True
except ImportError:
    RTL_AVAILABLE = False
    logger.warning("arabic-reshaper and python-bidi not available. Arabic RTL support disabled.")

def load_translations(language: str = 'en') -> Dict[str, Any]:
    """Load translation file for the specified language.
    
    Args:
        language: Language code ('en' or 'ar')
        
    Returns:
        Dictionary of translations
    """
    i18n_path = Path(__file__).parent.parent / 'i18n' / f'{language}.json'
    
    try:
        with open(i18n_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading translations for {language}: {e}")
        # Fallback to English
        if language != 'en':
            return load_translations('en')
        return {}

def get_translator(language: str = 'en') -> Dict[str, Any]:
    """Get translator function for the current language.
    
    Args:
        language: Language code ('en' or 'ar')
        
    Returns:
        Translation dictionary
    """
    return load_translations(language)

def render_arabic_text(text: str) -> str:
    """Render Arabic text with proper RTL support.
    
    Args:
        text: Arabic text to render
        
    Returns:
        RTL-formatted text
    """
    if RTL_AVAILABLE and 'arabic_reshaper' in globals() and 'get_display' in globals():
        reshaped_text = arabic_reshaper.reshape(text)  # type: ignore
        bidi_text = get_display(reshaped_text)  # type: ignore
        return str(bidi_text)
    return text

def set_language(language: str):
    """Set the application language.
    
    Args:
        language: Language code ('en' or 'ar')
    """
    st.session_state.language = language
    logger.info(f"Language changed to: {language}")

def setup_page():
    """Setup page configuration and CSS based on language."""
    language = st.session_state.get('language', 'en')
    
    # RTL CSS for Arabic
    if language == 'ar':
        st.markdown("""
            <style>
                .main .block-container {
                    direction: rtl;
                    text-align: right;
                }
                .stMarkdown, .stText {
                    direction: rtl;
                    text-align: right;
                }
                .stSelectbox label, .stRadio label, .stCheckbox label {
                    direction: rtl;
                    text-align: right;
                }
                /* Keep numbers LTR */
                .metric-value, .stMetric {
                    direction: ltr;
                    display: inline-block;
                }
            </style>
        """, unsafe_allow_html=True)
    
    # General CSS
    st.markdown("""
        <style>
            .stAlert {
                margin-top: 1rem;
                margin-bottom: 1rem;
            }
            .metric-container {
                background-color: #f0f2f6;
                padding: 1rem;
                border-radius: 0.5rem;
                margin-bottom: 1rem;
            }
            .segment-card {
                border: 1px solid #ddd;
                border-radius: 0.5rem;
                padding: 1rem;
                margin-bottom: 1rem;
                background-color: white;
            }
            .success-banner {
                background-color: #d4edda;
                border-color: #c3e6cb;
                color: #155724;
                padding: 1rem;
                border-radius: 0.5rem;
                margin-bottom: 1rem;
            }
            .warning-banner {
                background-color: #fff3cd;
                border-color: #ffc107;
                color: #856404;
                padding: 1rem;
                border-radius: 0.5rem;
                margin-bottom: 1rem;
            }
            .info-banner {
                background-color: #d1ecf1;
                border-color: #bee5eb;
                color: #0c5460;
                padding: 1rem;
                border-radius: 0.5rem;
                margin-bottom: 1rem;
            }
        </style>
    """, unsafe_allow_html=True)

def format_number(value: float, language: str = 'en', decimals: int = 2) -> str:
    """Format number according to language locale.
    
    Args:
        value: Number to format
        language: Language code ('en' or 'ar')
        decimals: Number of decimal places
        
    Returns:
        Formatted number string
    """
    if language == 'ar':
        # Arabic uses Arabic-Indic numerals in some contexts, but for consistency
        # we'll use Western Arabic numerals with RTL formatting
        formatted = f"{value:,.{decimals}f}"
        return f"\u200F{formatted}\u200E"  # RTL mark + number + LTR mark
    else:
        return f"{value:,.{decimals}f}"

def format_currency(value: float, currency: Optional[str] = None, language: str = 'en') -> str:
    """Format currency according to language and currency.
    
    Args:
        value: Amount to format
        currency: Currency code (None for generic format)
        language: Language code ('en' or 'ar')
        
    Returns:
        Formatted currency string
    """
    formatted_value = format_number(value, language, decimals=2)
    
    # If no currency specified, use generic format
    if currency is None:
        currency = ""  # Empty string for generic format
    
    if language == 'ar':
        return f"{formatted_value} {currency}".strip()
    else:
        return f"{currency} {formatted_value}".strip()

def format_percentage(value: float, language: str = 'en', decimals: int = 1) -> str:
    """Format percentage according to language.
    
    Args:
        value: Percentage value (0-100)
        language: Language code ('en' or 'ar')
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    formatted_value = format_number(value, language, decimals=decimals)
    return f"{formatted_value}%"

def show_metric_card(
    label: str,
    value: str,
    delta: str | None = None,
    help_text: str | None = None,
    language: str = 'en'
):
    """Display a metric card with optional delta and help text.
    
    Args:
        label: Metric label
        value: Metric value
        delta: Change indicator (optional)
        help_text: Help text (optional)
        language: Language code ('en' or 'ar')
    """
    if language == 'ar' and RTL_AVAILABLE:
        label = render_arabic_text(label)
        if help_text:
            help_text = render_arabic_text(help_text)
    
    st.metric(
        label=label,
        value=value,
        delta=delta,
        help=help_text
    )

def show_info_banner(message: str, banner_type: str = 'info', language: str = 'en'):
    """Display an information banner.
    
    Args:
        message: Message to display
        banner_type: Type of banner ('success', 'warning', 'info')
        language: Language code ('en' or 'ar')
    """
    if language == 'ar' and RTL_AVAILABLE:
        message = render_arabic_text(message)
    
    css_class = f"{banner_type}-banner"
    st.markdown(
        f'<div class="{css_class}">{message}</div>',
        unsafe_allow_html=True
    )

def show_download_button(
    data: bytes,
    filename: str,
    label: str,
    mime_type: str = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    language: str = 'en'
):
    """Display a download button.
    
    Args:
        data: File data as bytes
        filename: Filename for download
        label: Button label
        mime_type: MIME type of file
        language: Language code ('en' or 'ar')
    """
    if language == 'ar' and RTL_AVAILABLE:
        label = render_arabic_text(label)
    
    st.download_button(
        label=label,
        data=data,
        file_name=filename,
        mime=mime_type
    )

def create_segment_card(
    segment_name: str,
    segment_data: Dict[str, Any],
    translations: Dict[str, Any],
    language: str = 'en'
):
    """Create a card displaying segment information.
    
    Args:
        segment_name: Name of the segment
        segment_data: Segment statistics
        translations: Translation dictionary
        language: Language code ('en' or 'ar')
    """
    st.markdown('<div class="segment-card">', unsafe_allow_html=True)
    
    # Segment title
    segment_key = segment_name.lower().replace(' ', '_')
    segment_label = translations['segments'].get(segment_key, {}).get('name', segment_name)
    
    if language == 'ar' and RTL_AVAILABLE:
        segment_label = render_arabic_text(segment_label)
    
    st.markdown(f"### {segment_label}")
    
    # Segment description
    description = translations['segments'].get(segment_key, {}).get('description', '')
    if description:
        if language == 'ar' and RTL_AVAILABLE:
            description = render_arabic_text(description)
        st.markdown(f"*{description}*")
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        customers = segment_data.get('customer_count', 0)
        st.metric(
            translations['customers']['total_customers'],
            format_number(customers, language, decimals=0)
        )
    
    with col2:
        revenue = segment_data.get('total_revenue', 0)
        st.metric(
            translations['summary']['total_revenue'],
            format_currency(revenue, language=language)
        )
    
    with col3:
        avg_revenue = segment_data.get('avg_revenue_per_customer', 0)
        st.metric(
            translations['customers']['avg_revenue_per_customer'],
            format_currency(avg_revenue, language=language)
        )
    
    st.markdown('</div>', unsafe_allow_html=True)