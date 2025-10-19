"""Shared UI components for the Streamlit application."""

import streamlit as st
import json
from pathlib import Path
from typing import Dict, Any, Optional, Callable
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


# ============================================================================
# Page Protection & Error Handling
# ============================================================================

def require_data(func: Callable) -> Callable:
    """Decorator to ensure data is loaded before rendering page.
    
    Shows friendly empty state if no data is loaded, preventing errors.
    
    Usage:
        @require_data
        def render_my_page():
            # Page code here
    """
    def wrapper(*args, **kwargs):
        if not st.session_state.get('data_loaded', False):
            # Show friendly empty state
            language = st.session_state.get('language', 'en')
            
            st.markdown("""
            <div style="text-align: center; padding: 4rem 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        border-radius: 12px; color: white;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">📤</div>
                <h2 style="color: white; margin: 0;">No Data Loaded Yet</h2>
                <p style="font-size: 1.1rem; margin-top: 1rem; opacity: 0.9;">
                    Please upload your Salla data first to see insights
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Action button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("📤 Go to Upload Page", use_container_width=True, type="primary"):
                    st.session_state.page_selector = 'upload'
                    st.rerun()
            
            # Quick instructions
            st.markdown("---")
            st.markdown("""
            ### 🚀 Quick Start Guide
            
            1. **📥 Export Data** - Download your order data from Salla as Excel
            2. **📤 Upload** - Upload the Excel file on the Upload page
            3. **🔗 Map Columns** - Confirm column mappings (auto-detected)
            4. **📊 Analyze** - Explore insights, segments, and trends
            """)
            
            return None
        return func(*args, **kwargs)
    return wrapper


# ============================================================================
# Translation & Localization
# ============================================================================

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


def show_welcome_banner(language: str = 'en'):
    """Show welcome banner for first-time users.
    
    Args:
        language: Language code ('en' or 'ar')
    """
    # Check if user has seen welcome banner
    if st.session_state.get('welcome_seen', False):
        return
    
    t = get_translator(language)
    
    # Welcome message
    if language == 'ar':
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 2rem; border-radius: 10px; color: white; text-align: right; margin-bottom: 2rem;">
            <h2 style="margin: 0; color: white;">👋 مرحباً بك في التحليل المتقدم لسلة!</h2>
            <p style="font-size: 1.1rem; margin-top: 1rem; color: #f0f0f0;">
                اتبع هذه الخطوات الثلاث البسيطة:
            </p>
            <ol style="font-size: 1rem; color: #f0f0f0; margin-right: 1.5rem;">
                <li>📤 ارفع ملف Excel من سلة</li>
                <li>🔗 ربط الأعمدة (يتم تلقائياً)</li>
                <li>📊 استكشف الرؤى والتوصيات</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 2rem; border-radius: 10px; color: white; margin-bottom: 2rem;">
            <h2 style="margin: 0; color: white;">👋 Welcome to Advanced Analysis for Salla!</h2>
            <p style="font-size: 1.1rem; margin-top: 1rem; color: #f0f0f0;">
                Follow these 3 simple steps:
            </p>
            <ol style="font-size: 1rem; color: #f0f0f0;">
                <li>📤 Upload your Salla Excel export</li>
                <li>🔗 Map columns (auto-detected)</li>
                <li>📊 Explore insights & recommendations</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    # Dismiss button (no rerun - banner disappears on next natural render)
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("✓ Got it!" if language == 'en' else "✓ فهمت!", use_container_width=True, key="dismiss_welcome"):
            st.session_state.welcome_seen = True
            # No rerun needed - avoids conflicts with file upload


# ============================================================================
# Modern Design System Components
# ============================================================================

def app_header(title: str, subtitle: str = "", actions: list | None = None, language: str = 'en'):
    """Render a modern application header with optional action buttons.
    
    Args:
        title: Main title text
        subtitle: Optional subtitle/description
        actions: List of action button dictionaries with 'label', 'icon', 'callback' keys
        language: Language code ('en' or 'ar')
    """
    rtl_class = "rtl" if language == 'ar' else ""
    
    header_html = f"""
    <div class="modern-card {rtl_class}" style="margin-bottom: 2rem;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 style="margin: 0; font-size: 2.25rem; font-weight: 700; color: #111827;">
                    {title}
                </h1>
                {f'<p style="margin: 0.5rem 0 0 0; font-size: 1.125rem; color: #6B7280;">{subtitle}</p>' if subtitle else ''}
            </div>
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)
    
    # Render action buttons if provided
    if actions:
        cols = st.columns(len(actions))
        for idx, action in enumerate(actions):
            with cols[idx]:
                icon = action.get('icon', '')
                label = action.get('label', '')
                if st.button(f"{icon} {label}", key=f"header_action_{idx}", use_container_width=True):
                    if 'callback' in action and callable(action['callback']):
                        action['callback']()


def section(title: str, description: str = "", icon: str | None = None, language: str = 'en'):
    """Render a modern section header with optional icon and description.
    
    Args:
        title: Section title
        description: Optional description text
        icon: Optional emoji/icon
        language: Language code ('en' or 'ar')
    """
    rtl_class = "rtl" if language == 'ar' else ""
    
    section_html = f"""
    <div class="section-header {rtl_class}">
        {f'<span class="section-icon">{icon}</span>' if icon else ''}
        <div>
            <h2 class="section-title">{title}</h2>
            {f'<p class="section-description">{description}</p>' if description else ''}
        </div>
    </div>
    """
    st.markdown(section_html, unsafe_allow_html=True)


def kpi(title: str, value: str, delta: str | None = None, delta_color: str = "positive",
        help_text: str | None = None, language: str = 'en'):
    """Render a modern KPI card.
    
    Args:
        title: KPI title/label
        value: KPI value to display
        delta: Optional change indicator (e.g., "+12.5%")
        delta_color: Color of delta ("positive", "negative", or "neutral")
        help_text: Optional help tooltip text
        language: Language code ('en' or 'ar')
    """
    rtl_class = "rtl" if language == 'ar' else ""
    delta_class = f"kpi-delta {delta_color}" if delta else ""
    
    kpi_html = f"""
    <div class="kpi-card {rtl_class}">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        {f'<div class="{delta_class}">{delta}</div>' if delta else ''}
        {f'<div style="margin-top: 0.5rem; font-size: 0.875rem; color: #6B7280;">💡 {help_text}</div>' if help_text else ''}
    </div>
    """
    st.markdown(kpi_html, unsafe_allow_html=True)


def kpi_row(kpis: list, cols_per_row: int = 3, language: str = 'en'):
    """Render a row of KPI cards.
    
    Args:
        kpis: List of KPI dictionaries with keys: 'title', 'value', 'delta', 'delta_color', 'help'
        cols_per_row: Number of KPIs per row
        language: Language code ('en' or 'ar')
    """
    cols = st.columns(cols_per_row)
    for idx, kpi_data in enumerate(kpis):
        col_idx = idx % cols_per_row
        with cols[col_idx]:
            kpi(
                title=kpi_data.get('title', ''),
                value=kpi_data.get('value', ''),
                delta=kpi_data.get('delta'),
                delta_color=kpi_data.get('delta_color', 'positive'),
                help_text=kpi_data.get('help'),
                language=language
            )


def card(title: str | None = None, body_fn: Callable | None = None, footer: str | None = None, language: str = 'en'):
    """Render a modern card container.
    
    Args:
        title: Optional card title
        body_fn: Callable function that renders the card body content
        footer: Optional footer text
        language: Language code ('en' or 'ar')
    """
    rtl_class = "rtl" if language == 'ar' else ""
    
    # Start card
    if title:
        st.markdown(f'<div class="modern-card {rtl_class}"><div class="card-header">{title}</div><div class="card-body">', 
                   unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="modern-card {rtl_class}"><div class="card-body">', 
                   unsafe_allow_html=True)
    
    # Render body content
    if body_fn and callable(body_fn):
        body_fn()
    
    # End card
    if footer:
        st.markdown(f'</div><div class="card-footer">{footer}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('</div></div>', unsafe_allow_html=True)


def stepper(current_step: int, steps: list, language: str = 'en'):
    """Render a modern stepper component.
    
    Args:
        current_step: Current active step (1-indexed)
        steps: List of step labels
        language: Language code ('en' or 'ar')
    """
    rtl_class = "rtl" if language == 'ar' else ""
    
    stepper_html = f'<div class="stepper-container {rtl_class}">'
    
    for idx, step_label in enumerate(steps, 1):
        step_class = ""
        if idx < current_step:
            step_class = "completed"
        elif idx == current_step:
            step_class = "active"
        
        bubble_content = "✓" if idx < current_step else str(idx)
        
        stepper_html += f'''
        <div class="stepper-step {step_class}">
            <div class="stepper-bubble">{bubble_content}</div>
            <div class="stepper-label">{step_label}</div>
        </div>
        '''
    
    stepper_html += '</div>'
    st.markdown(stepper_html, unsafe_allow_html=True)


def language_toggle(current_lang: str = 'en', on_change: Callable | None = None):
    """Render a language toggle button.
    
    Args:
        current_lang: Current language code
        on_change: Callback function when language changes
    """
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🇬🇧 English", 
                    use_container_width=True,
                    type="primary" if current_lang == 'en' else "secondary",
                    key="lang_en"):
            if current_lang != 'en':
                st.session_state.language = 'en'
                st.session_state.rtl = False
                if on_change:
                    on_change('en')
                st.rerun()
    
    with col2:
        if st.button("🇸🇦 العربية", 
                    use_container_width=True,
                    type="primary" if current_lang == 'ar' else "secondary",
                    key="lang_ar"):
            if current_lang != 'ar':
                st.session_state.language = 'ar'
                st.session_state.rtl = True
                if on_change:
                    on_change('ar')
                st.rerun()


def empty_state(title: str, description: str, cta_label: str | None = None,
                cta_callback: Callable | None = None, icon: str = "📭", language: str = 'en'):
    """Render an empty state component.
    
    Args:
        title: Empty state title
        description: Description text
        cta_label: Optional call-to-action button label
        cta_callback: Optional callback for CTA button
        icon: Emoji/icon to display
        language: Language code ('en' or 'ar')
    """
    rtl_class = "rtl" if language == 'ar' else ""
    
    empty_html = f"""
    <div class="empty-state {rtl_class}">
        <div class="empty-state-icon">{icon}</div>
        <div class="empty-state-title">{title}</div>
        <div class="empty-state-description">{description}</div>
    </div>
    """
    st.markdown(empty_html, unsafe_allow_html=True)
    
    if cta_label and cta_callback:
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button(cta_label, use_container_width=True, type="primary"):
                cta_callback()


def toast_success(message: str, duration: int = 3):
    """Show a success toast notification.
    
    Args:
        message: Success message
        duration: Display duration in seconds
    """
    st.success(f"✅ {message}", icon="✅")


def toast_error(message: str):
    """Show an error toast notification.
    
    Args:
        message: Error message
    """
    st.error(f"❌ {message}", icon="🚨")


def toast_info(message: str):
    """Show an info toast notification.
    
    Args:
        message: Info message
    """
    st.info(f"ℹ️ {message}", icon="ℹ️")


def skeleton_loader(lines: int = 3):
    """Render a skeleton loading placeholder.
    
    Args:
        lines: Number of skeleton lines to render
    """
    skeleton_html = '<div style="padding: 1rem;">'
    skeleton_html += '<div class="skeleton skeleton-title"></div>'
    for _ in range(lines):
        skeleton_html += '<div class="skeleton skeleton-text"></div>'
    skeleton_html += '</div>'
    
    st.markdown(skeleton_html, unsafe_allow_html=True)


def badge(text: str, variant: str = "neutral", language: str = 'en'):
    """Render a badge component.
    
    Args:
        text: Badge text
        variant: Badge style variant ("success", "warning", "error", "info", "neutral")
        language: Language code ('en' or 'ar')
    
    Returns:
        HTML string for the badge
    """
    rtl_class = "rtl" if language == 'ar' else ""
    return f'<span class="badge badge-{variant} {rtl_class}">{text}</span>'


def progress_bar(value: float, max_value: float = 100, label: str = "", color: str = "primary"):
    """Render a modern progress bar.
    
    Args:
        value: Current progress value
        max_value: Maximum value (default 100)
        label: Optional label text
        color: Progress bar color ("primary", "success", "warning", "error")
    """
    percentage = (value / max_value) * 100 if max_value > 0 else 0
    
    color_map = {
        "primary": "#7C3AED",
        "success": "#10B981",
        "warning": "#F59E0B",
        "error": "#EF4444"
    }
    
    bar_color = color_map.get(color, color_map["primary"])
    
    progress_html = f"""
    <div style="margin: 1rem 0;">
        {f'<div style="margin-bottom: 0.5rem; font-size: 0.875rem; color: #6B7280; font-weight: 500;">{label}</div>' if label else ''}
        <div style="background: #E5E7EB; border-radius: 9999px; height: 8px; overflow: hidden;">
            <div style="background: {bar_color}; height: 100%; width: {percentage}%; transition: width 0.3s ease;"></div>
        </div>
        <div style="margin-top: 0.25rem; font-size: 0.75rem; color: #9CA3AF; text-align: right;">
            {value:.1f} / {max_value} ({percentage:.1f}%)
        </div>
    </div>
    """
    st.markdown(progress_html, unsafe_allow_html=True)