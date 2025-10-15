"""Mobile detection and responsive layout utilities."""

import streamlit as st
from typing import Tuple, Optional, List


def is_mobile() -> bool:
    """
    Detect if user is on a mobile device.
    
    This is a heuristic based on typical mobile screen widths.
    Streamlit doesn't have direct device detection, so we use JavaScript injection.
    """
    # Try to get screen width from session state if already detected
    if 'screen_width' in st.session_state:
        return st.session_state.screen_width < 768
    
    # Default to False (assume desktop) if not detected
    return False


def get_responsive_columns(desktop_cols: int = 3, tablet_cols: int = 2, mobile_cols: int = 1) -> int:
    """
    Get appropriate number of columns based on screen size.
    
    Args:
        desktop_cols: Number of columns for desktop (>= 1024px)
        tablet_cols: Number of columns for tablet (768-1023px)
        mobile_cols: Number of columns for mobile (< 768px)
    
    Returns:
        Number of columns to use
    """
    screen_width = st.session_state.get('screen_width', 1920)  # Default to desktop
    
    if screen_width < 768:
        return mobile_cols
    elif screen_width < 1024:
        return tablet_cols
    else:
        return desktop_cols


def inject_screen_detector():
    """
    Inject JavaScript to detect screen width and store in session state.
    
    This should be called once at the start of the app.
    """
    # Only inject once per session
    if 'screen_detection_injected' not in st.session_state:
        st.session_state.screen_detection_injected = True
        
        # Try to read from experimental query params (Streamlit limitation)
        # For now, we'll use a simple heuristic: check if user agent suggests mobile
        try:
            # This is a fallback - actual detection would need custom component
            # Default to desktop for now
            st.session_state.screen_width = 1920
        except:
            st.session_state.screen_width = 1920


def get_mobile_layout_config() -> dict:
    """
    Get layout configuration for mobile devices.
    
    Returns:
        Dictionary with layout settings
    """
    if is_mobile():
        return {
            'show_sidebar_by_default': False,
            'use_single_column': True,
            'chart_height': 300,
            'table_page_size': 5,
            'hide_complex_charts': True,
            'simplified_navigation': True
        }
    else:
        return {
            'show_sidebar_by_default': True,
            'use_single_column': False,
            'chart_height': 400,
            'table_page_size': 10,
            'hide_complex_charts': False,
            'simplified_navigation': False
        }


def mobile_metric_card(label: str, value: str, delta: Optional[str] = None, help_text: Optional[str] = None):
    """
    Display a metric card optimized for mobile.
    
    Args:
        label: Metric label
        value: Metric value
        delta: Optional delta/change indicator
        help_text: Optional help text
    """
    if is_mobile():
        # Compact mobile layout
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 8px;
            color: white;
        ">
            <div style="font-size: 11px; opacity: 0.9; margin-bottom: 4px;">{label}</div>
            <div style="font-size: 20px; font-weight: bold;">{value}</div>
            {f'<div style="font-size: 12px; margin-top: 4px;">{delta}</div>' if delta else ''}
        </div>
        """, unsafe_allow_html=True)
    else:
        # Standard desktop metric
        st.metric(label=label, value=value, delta=delta, help=help_text)


def responsive_columns(*ratios) -> List:
    """
    Create responsive columns that collapse to single column on mobile.
    
    Args:
        *ratios: Column ratios (e.g., 1, 2, 1 for three columns)
    
    Returns:
        List of column objects
    """
    if is_mobile():
        # On mobile, return single column
        return [st.container()]
    else:
        # On desktop, use specified ratios
        return st.columns(ratios)


def mobile_friendly_chart_config() -> dict:
    """
    Get Plotly chart configuration optimized for mobile.
    
    Returns:
        Dictionary of Plotly config options
    """
    if is_mobile():
        return {
            'displayModeBar': False,  # Hide toolbar on mobile
            'responsive': True,
            'displaylogo': False,
        }
    else:
        return {
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
        }


def show_mobile_tip():
    """Show a tip for mobile users about rotating to landscape."""
    if is_mobile():
        st.info("📱 **Tip:** Rotate your device to landscape mode for a better viewing experience!")
