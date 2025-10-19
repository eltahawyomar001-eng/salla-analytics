"""Modern design system theme for Advanced Analysis for Salla.

This module provides:
- Design tokens (colors, spacing, shadows, typography)
- CSS injection for modern UI components
- Theme consistency across the application
"""

import streamlit as st
from typing import Dict, Any

# Design Tokens
DESIGN_TOKENS: Dict[str, Any] = {
    # Brand Colors
    "colors": {
        "primary": "#7C3AED",  # Purple
        "primary_dark": "#6D28D9",
        "secondary": "#2563EB",  # Blue
        "secondary_dark": "#1D4ED8",
        "success": "#10B981",
        "success_bg": "#D1FAE5",
        "warning": "#F59E0B",
        "warning_bg": "#FEF3C7",
        "error": "#EF4444",
        "error_bg": "#FEE2E2",
        "info": "#3B82F6",
        "info_bg": "#DBEAFE",
        
        # Neutral palette
        "gray_50": "#F9FAFB",
        "gray_100": "#F3F4F6",
        "gray_200": "#E5E7EB",
        "gray_300": "#D1D5DB",
        "gray_400": "#9CA3AF",
        "gray_500": "#6B7280",
        "gray_600": "#4B5563",
        "gray_700": "#374151",
        "gray_800": "#1F2937",
        "gray_900": "#111827",
        
        # Gradients
        "gradient_primary": "linear-gradient(135deg, #7C3AED 0%, #2563EB 100%)",
        "gradient_success": "linear-gradient(135deg, #10B981 0%, #059669 100%)",
        "gradient_purple": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "gradient_sunset": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
    },
    
    # Spacing (based on 4px grid)
    "spacing": {
        "xs": "0.25rem",   # 4px
        "sm": "0.5rem",    # 8px
        "md": "1rem",      # 16px
        "lg": "1.5rem",    # 24px
        "xl": "2rem",      # 32px
        "2xl": "3rem",     # 48px
        "3xl": "4rem",     # 64px
    },
    
    # Border radius
    "radius": {
        "sm": "0.375rem",  # 6px
        "md": "0.5rem",    # 8px
        "lg": "0.75rem",   # 12px
        "xl": "1rem",      # 16px
        "2xl": "1.5rem",   # 24px
        "full": "9999px",
    },
    
    # Shadows
    "shadow": {
        "sm": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
        "md": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
        "lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
        "xl": "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
        "card": "0 4px 24px rgba(0, 0, 0, 0.08)",
        "hover": "0 12px 28px rgba(0, 0, 0, 0.12)",
    },
    
    # Typography
    "typography": {
        "font_family": "'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif",
        "font_size_xs": "0.75rem",   # 12px
        "font_size_sm": "0.875rem",  # 14px
        "font_size_base": "1rem",    # 16px
        "font_size_lg": "1.125rem",  # 18px
        "font_size_xl": "1.25rem",   # 20px
        "font_size_2xl": "1.5rem",   # 24px
        "font_size_3xl": "1.875rem", # 30px
        "font_size_4xl": "2.25rem",  # 36px
        
        "line_height_tight": "1.25",
        "line_height_normal": "1.5",
        "line_height_relaxed": "1.75",
        
        "font_weight_normal": "400",
        "font_weight_medium": "500",
        "font_weight_semibold": "600",
        "font_weight_bold": "700",
    },
    
    # Container widths
    "container": {
        "sm": "640px",
        "md": "768px",
        "lg": "1024px",
        "xl": "1280px",
        "2xl": "1536px",
    },
    
    # Z-index layers
    "z_index": {
        "dropdown": "1000",
        "sticky": "1020",
        "fixed": "1030",
        "modal_backdrop": "1040",
        "modal": "1050",
        "popover": "1060",
        "tooltip": "1070",
    },
}


def inject_theme_css() -> None:
    """Inject comprehensive theme CSS into the Streamlit app.
    
    This function should be called once at app startup to apply
    the modern design system styling.
    """
    tokens = DESIGN_TOKENS
    colors = tokens["colors"]
    spacing = tokens["spacing"]
    radius = tokens["radius"]
    shadow = tokens["shadow"]
    typo = tokens["typography"]
    
    css = f"""
    <style>
    /* ============================================
       CSS Variables for Theme Consistency
       ============================================ */
    :root {{
        /* Colors */
        --primary: {colors['primary']};
        --primary-dark: {colors['primary_dark']};
        --secondary: {colors['secondary']};
        --secondary-dark: {colors['secondary_dark']};
        --success: {colors['success']};
        --success-bg: {colors['success_bg']};
        --warning: {colors['warning']};
        --warning-bg: {colors['warning_bg']};
        --error: {colors['error']};
        --error-bg: {colors['error_bg']};
        --info: {colors['info']};
        --info-bg: {colors['info_bg']};
        
        /* Neutral colors */
        --gray-50: {colors['gray_50']};
        --gray-100: {colors['gray_100']};
        --gray-200: {colors['gray_200']};
        --gray-300: {colors['gray_300']};
        --gray-400: {colors['gray_400']};
        --gray-500: {colors['gray_500']};
        --gray-600: {colors['gray_600']};
        --gray-700: {colors['gray_700']};
        --gray-800: {colors['gray_800']};
        --gray-900: {colors['gray_900']};
        
        /* Spacing */
        --spacing-xs: {spacing['xs']};
        --spacing-sm: {spacing['sm']};
        --spacing-md: {spacing['md']};
        --spacing-lg: {spacing['lg']};
        --spacing-xl: {spacing['xl']};
        --spacing-2xl: {spacing['2xl']};
        
        /* Border radius */
        --radius-sm: {radius['sm']};
        --radius-md: {radius['md']};
        --radius-lg: {radius['lg']};
        --radius-xl: {radius['xl']};
        --radius-2xl: {radius['2xl']};
        
        /* Shadows */
        --shadow-sm: {shadow['sm']};
        --shadow-md: {shadow['md']};
        --shadow-lg: {shadow['lg']};
        --shadow-card: {shadow['card']};
        --shadow-hover: {shadow['hover']};
        
        /* Typography */
        --font-family: {typo['font_family']};
        --font-size-xs: {typo['font_size_xs']};
        --font-size-sm: {typo['font_size_sm']};
        --font-size-base: {typo['font_size_base']};
        --font-size-lg: {typo['font_size_lg']};
        --font-size-xl: {typo['font_size_xl']};
        --font-size-2xl: {typo['font_size_2xl']};
        --font-size-3xl: {typo['font_size_3xl']};
    }}
    
    /* ============================================
       Global Resets and Base Styles
       ============================================ */
    * {{
        font-family: var(--font-family) !important;
    }}
    
    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }}
    
    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* ============================================
       Modern Card Styling
       ============================================ */
    .modern-card {{
        background: white;
        border-radius: var(--radius-xl);
        padding: var(--spacing-lg);
        box-shadow: var(--shadow-card);
        margin-bottom: var(--spacing-md);
        transition: all 0.3s ease;
        border: 1px solid var(--gray-100);
    }}
    
    .modern-card:hover {{
        box-shadow: var(--shadow-hover);
        transform: translateY(-2px);
    }}
    
    .card-header {{
        font-size: var(--font-size-xl);
        font-weight: 600;
        color: var(--gray-900);
        margin-bottom: var(--spacing-md);
        padding-bottom: var(--spacing-sm);
        border-bottom: 2px solid var(--gray-100);
    }}
    
    .card-body {{
        color: var(--gray-700);
        line-height: 1.6;
    }}
    
    .card-footer {{
        margin-top: var(--spacing-md);
        padding-top: var(--spacing-md);
        border-top: 1px solid var(--gray-100);
        font-size: var(--font-size-sm);
        color: var(--gray-500);
    }}
    
    /* ============================================
       KPI Cards
       ============================================ */
    .kpi-card {{
        background: white;
        border-radius: var(--radius-lg);
        padding: var(--spacing-lg);
        box-shadow: var(--shadow-md);
        border-left: 4px solid var(--primary);
        transition: all 0.3s ease;
    }}
    
    .kpi-card:hover {{
        box-shadow: var(--shadow-lg);
        transform: translateY(-2px);
    }}
    
    .kpi-title {{
        font-size: var(--font-size-sm);
        color: var(--gray-600);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: var(--spacing-xs);
    }}
    
    .kpi-value {{
        font-size: var(--font-size-3xl);
        font-weight: 700;
        color: var(--gray-900);
        margin-bottom: var(--spacing-xs);
        line-height: 1.2;
    }}
    
    .kpi-delta {{
        font-size: var(--font-size-sm);
        font-weight: 500;
    }}
    
    .kpi-delta.positive {{
        color: var(--success);
    }}
    
    .kpi-delta.negative {{
        color: var(--error);
    }}
    
    /* ============================================
       Section Headers
       ============================================ */
    .section-header {{
        margin-bottom: var(--spacing-lg);
        padding-bottom: var(--spacing-sm);
        border-bottom: 3px solid var(--primary);
        display: flex;
        align-items: center;
        gap: var(--spacing-sm);
    }}
    
    .section-title {{
        font-size: var(--font-size-2xl);
        font-weight: 700;
        color: var(--gray-900);
        margin: 0;
    }}
    
    .section-description {{
        font-size: var(--font-size-base);
        color: var(--gray-600);
        margin-top: var(--spacing-xs);
        line-height: 1.6;
    }}
    
    .section-icon {{
        font-size: var(--font-size-3xl);
    }}
    
    /* ============================================
       Buttons - Enhanced Styling
       ============================================ */
    .stButton > button {{
        border-radius: var(--radius-lg);
        font-weight: 600;
        padding: 0.625rem 1.5rem;
        transition: all 0.2s ease;
        border: none;
        box-shadow: var(--shadow-sm);
        font-size: var(--font-size-base);
    }}
    
    .stButton > button:hover {{
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
    }}
    
    .stButton > button[kind="primary"] {{
        background: {colors['gradient_primary']};
        color: white;
    }}
    
    .stButton > button[kind="primary"]:hover {{
        filter: brightness(1.1);
    }}
    
    .stButton > button[kind="secondary"] {{
        background: var(--gray-100);
        color: var(--gray-700);
    }}
    
    .stButton > button[kind="secondary"]:hover {{
        background: var(--gray-200);
    }}
    
    /* ============================================
       File Uploader - Dropzone Style
       ============================================ */
    .uploadedFile {{
        display: none !important;
    }}
    
    [data-testid="stFileUploader"] {{
        background: var(--gray-50);
        border: 3px dashed var(--gray-300);
        border-radius: var(--radius-xl);
        padding: var(--spacing-2xl);
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
    }}
    
    [data-testid="stFileUploader"]:hover {{
        border-color: var(--primary);
        background: var(--gray-100);
        box-shadow: var(--shadow-lg);
        transform: scale(1.01);
    }}
    
    [data-testid="stFileUploader"] section {{
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: var(--spacing-md);
    }}
    
    [data-testid="stFileUploader"] section::before {{
        content: "📁";
        font-size: 4rem;
        display: block;
    }}
    
    [data-testid="stFileUploader"] small {{
        font-size: var(--font-size-sm);
        color: var(--gray-500);
    }}
    
    /* ============================================
       Stepper Component
       ============================================ */
    .stepper-container {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: var(--spacing-xl) 0;
        padding: var(--spacing-lg);
        background: var(--gray-50);
        border-radius: var(--radius-xl);
    }}
    
    .stepper-step {{
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        position: relative;
    }}
    
    .stepper-step:not(:last-child)::after {{
        content: '';
        position: absolute;
        top: 20px;
        left: calc(50% + 30px);
        width: calc(100% - 60px);
        height: 3px;
        background: var(--gray-300);
        z-index: 0;
    }}
    
    .stepper-step.active:not(:last-child)::after {{
        background: var(--primary);
    }}
    
    .stepper-bubble {{
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: var(--gray-300);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: var(--font-size-lg);
        margin-bottom: var(--spacing-sm);
        z-index: 1;
        position: relative;
        transition: all 0.3s ease;
    }}
    
    .stepper-step.active .stepper-bubble {{
        background: {colors['gradient_primary']};
        box-shadow: var(--shadow-lg);
        transform: scale(1.1);
    }}
    
    .stepper-step.completed .stepper-bubble {{
        background: var(--success);
    }}
    
    .stepper-label {{
        font-size: var(--font-size-sm);
        color: var(--gray-600);
        font-weight: 500;
        text-align: center;
    }}
    
    .stepper-step.active .stepper-label {{
        color: var(--primary);
        font-weight: 600;
    }}
    
    /* ============================================
       Badges
       ============================================ */
    .badge {{
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: var(--radius-full);
        font-size: var(--font-size-xs);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    
    .badge-success {{
        background: var(--success-bg);
        color: var(--success);
    }}
    
    .badge-warning {{
        background: var(--warning-bg);
        color: var(--warning);
    }}
    
    .badge-error {{
        background: var(--error-bg);
        color: var(--error);
    }}
    
    .badge-info {{
        background: var(--info-bg);
        color: var(--info);
    }}
    
    .badge-neutral {{
        background: var(--gray-100);
        color: var(--gray-700);
    }}
    
    /* ============================================
       Tables - Modern Styling
       ============================================ */
    .dataframe {{
        border-radius: var(--radius-lg) !important;
        overflow: hidden;
        box-shadow: var(--shadow-card);
        border: 1px solid var(--gray-200);
    }}
    
    .dataframe thead th {{
        background: {colors['gradient_primary']} !important;
        color: white !important;
        font-weight: 600;
        padding: 1rem !important;
        text-transform: uppercase;
        font-size: var(--font-size-xs);
        letter-spacing: 0.05em;
        position: sticky;
        top: 0;
        z-index: 10;
    }}
    
    .dataframe tbody tr {{
        transition: background 0.2s ease;
    }}
    
    .dataframe tbody tr:hover {{
        background: var(--gray-50);
    }}
    
    .dataframe tbody td {{
        padding: 0.875rem 1rem !important;
        border-bottom: 1px solid var(--gray-100);
        color: var(--gray-700);
    }}
    
    .dataframe tbody tr:last-child td {{
        border-bottom: none;
    }}
    
    /* ============================================
       Empty State
       ============================================ */
    .empty-state {{
        text-align: center;
        padding: var(--spacing-3xl);
        background: var(--gray-50);
        border-radius: var(--radius-xl);
        border: 2px dashed var(--gray-300);
    }}
    
    .empty-state-icon {{
        font-size: 4rem;
        margin-bottom: var(--spacing-md);
        opacity: 0.5;
    }}
    
    .empty-state-title {{
        font-size: var(--font-size-xl);
        font-weight: 600;
        color: var(--gray-700);
        margin-bottom: var(--spacing-sm);
    }}
    
    .empty-state-description {{
        font-size: var(--font-size-base);
        color: var(--gray-500);
        margin-bottom: var(--spacing-lg);
        line-height: 1.6;
    }}
    
    /* ============================================
       Toast Notifications
       ============================================ */
    .toast {{
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        padding: var(--spacing-md) var(--spacing-lg);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-xl);
        display: flex;
        align-items: center;
        gap: var(--spacing-sm);
        animation: slideIn 0.3s ease;
        max-width: 400px;
    }}
    
    @keyframes slideIn {{
        from {{
            transform: translateX(400px);
            opacity: 0;
        }}
        to {{
            transform: translateX(0);
            opacity: 1;
        }}
    }}
    
    .toast-success {{
        background: var(--success);
        color: white;
    }}
    
    .toast-error {{
        background: var(--error);
        color: white;
    }}
    
    .toast-info {{
        background: var(--info);
        color: white;
    }}
    
    /* ============================================
       Sidebar Improvements
       ============================================ */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
    }}
    
    [data-testid="stSidebar"] .block-container {{
        padding-top: 2rem;
    }}
    
    /* ============================================
       RTL Support
       ============================================ */
    .rtl {{
        direction: rtl;
        text-align: right;
    }}
    
    .rtl .modern-card,
    .rtl .kpi-card {{
        border-left: none;
        border-right: 4px solid var(--primary);
    }}
    
    .rtl .section-header {{
        flex-direction: row-reverse;
    }}
    
    /* ============================================
       Metric Cards (Streamlit native)
       ============================================ */
    [data-testid="stMetric"] {{
        background: white;
        padding: var(--spacing-lg);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-card);
        border-left: 4px solid var(--primary);
    }}
    
    [data-testid="stMetricLabel"] {{
        font-size: var(--font-size-sm);
        color: var(--gray-600);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    
    [data-testid="stMetricValue"] {{
        font-size: var(--font-size-3xl);
        font-weight: 700;
        color: var(--gray-900);
    }}
    
    [data-testid="stMetricDelta"] {{
        font-size: var(--font-size-sm);
        font-weight: 600;
    }}
    
    /* ============================================
       Expander Styling
       ============================================ */
    .streamlit-expanderHeader {{
        background: var(--gray-50);
        border-radius: var(--radius-lg);
        padding: var(--spacing-md);
        font-weight: 600;
        color: var(--gray-800);
        border: 1px solid var(--gray-200);
    }}
    
    .streamlit-expanderHeader:hover {{
        background: var(--gray-100);
        border-color: var(--primary);
    }}
    
    /* ============================================
       Tabs Styling
       ============================================ */
    .stTabs [data-baseweb="tab-list"] {{
        gap: var(--spacing-sm);
        background: var(--gray-50);
        padding: var(--spacing-sm);
        border-radius: var(--radius-lg);
    }}
    
    .stTabs [data-baseweb="tab"] {{
        border-radius: var(--radius-md);
        padding: var(--spacing-sm) var(--spacing-lg);
        font-weight: 500;
        transition: all 0.2s ease;
    }}
    
    .stTabs [data-baseweb="tab"]:hover {{
        background: var(--gray-200);
    }}
    
    .stTabs [aria-selected="true"] {{
        background: white !important;
        box-shadow: var(--shadow-sm);
        font-weight: 600;
    }}
    
    /* ============================================
       Loading Skeleton
       ============================================ */
    .skeleton {{
        background: linear-gradient(90deg, var(--gray-200) 0%, var(--gray-100) 50%, var(--gray-200) 100%);
        background-size: 200% 100%;
        animation: loading 1.5s infinite;
        border-radius: var(--radius-md);
    }}
    
    @keyframes loading {{
        0% {{ background-position: 200% 0; }}
        100% {{ background-position: -200% 0; }}
    }}
    
    .skeleton-text {{
        height: 1rem;
        margin-bottom: var(--spacing-sm);
    }}
    
    .skeleton-title {{
        height: 2rem;
        margin-bottom: var(--spacing-md);
        width: 60%;
    }}
    
    /* ============================================
       Responsive Design
       ============================================ */
    @media (max-width: 768px) {{
        .main .block-container {{
            padding: var(--spacing-md);
        }}
        
        .kpi-value {{
            font-size: var(--font-size-2xl);
        }}
        
        .section-title {{
            font-size: var(--font-size-xl);
        }}
        
        .stepper-container {{
            flex-direction: column;
            gap: var(--spacing-md);
        }}
        
        .stepper-step:not(:last-child)::after {{
            display: none;
        }}
    }}
    
    /* ============================================
       Accessibility Enhancements
       ============================================ */
    *:focus-visible {{
        outline: 3px solid var(--primary);
        outline-offset: 2px;
    }}
    
    button:focus-visible,
    a:focus-visible {{
        outline: 3px solid var(--primary);
        outline-offset: 2px;
    }}
    
    /* ============================================
       Print Styles
       ============================================ */
    @media print {{
        .stButton, [data-testid="stSidebar"] {{
            display: none !important;
        }}
        
        .modern-card {{
            box-shadow: none;
            border: 1px solid var(--gray-300);
            page-break-inside: avoid;
        }}
    }}
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)


def get_theme_tokens() -> Dict[str, Any]:
    """Get the design tokens dictionary.
    
    Returns:
        Dictionary containing all design tokens
    """
    return DESIGN_TOKENS
