# 🎨 Modern Design System - Component Reference

## Quick Import Guide

```python
# Theme System
from app.ui.theme import inject_theme_css, get_theme_tokens, DESIGN_TOKENS

# Modern Components
from app.ui.components import (
    app_header,      # Page headers
    section,         # Section dividers
    kpi, kpi_row,    # KPI metrics
    card,            # Card containers
    stepper,         # Wizard steps
    language_toggle, # EN/AR switcher
    empty_state,     # Empty views
    toast_success, toast_error, toast_info,  # Notifications
    skeleton_loader, # Loading states
    badge,           # Status badges
    progress_bar     # Progress indicators
)

# Chart Helpers
from app.ui.charts import (
    line_trend,      # Line charts
    bar_compare,     # Bar charts
    pie_distribution,# Pie/Donut charts
    cohort_heatmap,  # Heatmaps
    scatter_plot,    # Scatter plots
    area_chart,      # Area charts
    funnel_chart,    # Funnels
    gauge_chart      # Gauges
)
```

---

## 📖 Component Usage Examples

### 1. App Header
```python
app_header(
    title="Executive Summary",
    subtitle="Overview of your store performance for January 2025",
    actions=[
        {
            "label": "Export Report",
            "icon": "📥",
            "callback": lambda: export_data()
        }
    ],
    language=st.session_state.language
)
```

**Output:**
```
╔═══════════════════════════════════════════════════╗
║ Executive Summary                         [📥 Export Report] ║
║ Overview of your store performance for Jan 2025          ║
╚═══════════════════════════════════════════════════╝
```

---

### 2. Section Headers
```python
section(
    title="Financial Performance",
    description="Revenue, profit, and growth metrics",
    icon="💰",
    language=st.session_state.language
)
```

**Output:**
```
💰 Financial Performance
   ════════════════════════
   Revenue, profit, and growth metrics
```

---

### 3. KPI Cards

**Single KPI:**
```python
kpi(
    title="Total Revenue",
    value="SAR 245,680",
    delta="+12.5% vs last month",
    delta_color="positive",
    help_text="Includes all completed orders",
    language=st.session_state.language
)
```

**KPI Row (Grid):**
```python
kpi_row(
    kpis=[
        {
            "title": "Orders Today",
            "value": "1,234",
            "delta": "+8.2%",
            "delta_color": "positive",
            "help": "Compared to yesterday"
        },
        {
            "title": "Revenue Today",
            "value": "SAR 45,670",
            "delta": "+5.3%",
            "delta_color": "positive"
        },
        {
            "title": "Refund Rate",
            "value": "2.4%",
            "delta": "-0.8%",
            "delta_color": "positive",
            "help": "Lower is better"
        }
    ],
    cols_per_row=3,
    language=st.session_state.language
)
```

**Output:**
```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ ORDERS TODAY│  │REVENUE TODAY│  │ REFUND RATE │
│             │  │             │  │             │
│    1,234    │  │ SAR 45,670  │  │    2.4%     │
│   +8.2% ↑   │  │   +5.3% ↑   │  │   -0.8% ↓   │
│ vs yesterday│  │             │  │ Lower=better│
└─────────────┘  └─────────────┘  └─────────────┘
```

---

### 4. Card Containers
```python
def render_chart():
    # Your chart code here
    st.plotly_chart(fig, use_container_width=True)

card(
    title="Monthly Revenue Trend",
    body_fn=render_chart,
    footer="Data updated 5 minutes ago",
    language=st.session_state.language
)
```

---

### 5. Stepper (Wizard)
```python
stepper(
    current_step=2,
    steps=["Upload File", "Map Columns", "Review & Process"],
    language=st.session_state.language
)
```

**Output:**
```
┌───┐────────┌───┐────────┌───┐
│ ✓ │━━━━━━━━│ 2 │        │ 3 │
└───┘        └───┘        └───┘
Upload File  Map Columns  Review
(completed)  (active)     (pending)
```

---

### 6. Language Toggle
```python
language_toggle(
    current_lang=st.session_state.language,
    on_change=lambda lang: set_language(lang)
)
```

**Output:**
```
┌─────────────┬─────────────┐
│ 🇬🇧 English │ 🇸🇦 العربية │
│  (active)   │  (inactive) │
└─────────────┴─────────────┘
```

---

### 7. Empty States
```python
empty_state(
    title="No Data Yet",
    description="Upload your first Salla export file to get started with analytics.",
    cta_label="Upload Now",
    cta_callback=lambda: st.session_state.update({"page": "upload"}),
    icon="📭",
    language=st.session_state.language
)
```

**Output:**
```
        📭
    No Data Yet
    
Upload your first Salla export
file to get started with analytics.

    [Upload Now]
```

---

### 8. Toasts (Notifications)
```python
# Success
toast_success("Data uploaded successfully!")

# Error
toast_error("Failed to process file. Please check format.")

# Info
toast_info("Analysis will take approximately 2 minutes.")
```

---

### 9. Badges
```python
st.markdown(badge("Completed", "success"))
st.markdown(badge("Pending", "warning"))
st.markdown(badge("Failed", "error"))
st.markdown(badge("In Progress", "info"))
```

**Output:**
```
[✓ Completed]  [⚠ Pending]  [✗ Failed]  [ℹ In Progress]
(green)        (yellow)     (red)       (blue)
```

---

### 10. Progress Bar
```python
progress_bar(
    value=75,
    max_value=100,
    label="Processing Orders",
    color="primary"
)
```

**Output:**
```
Processing Orders
[████████████████████░░░░░░░] 75 / 100 (75.0%)
```

---

## 🎨 Chart Examples

### Line Trend
```python
from app.ui.charts import line_trend

fig = line_trend(
    df=monthly_data,
    x="month",
    y="revenue",
    title="Monthly Revenue Trend",
    x_label="Month",
    y_label="Revenue (SAR)",
    show_markers=True,
    smooth=True,
    height=500
)

st.plotly_chart(fig, use_container_width=True)
```

### Bar Comparison
```python
from app.ui.charts import bar_compare

fig = bar_compare(
    df=product_data,
    x="product_name",
    y="units_sold",
    title="Top 10 Products by Units Sold",
    orientation='h',  # Horizontal bars
    show_values=True,
    height=600
)

st.plotly_chart(fig, use_container_width=True)
```

### Cohort Heatmap
```python
from app.ui.charts import cohort_heatmap

fig = cohort_heatmap(
    df=cohort_data,
    x="period",
    y="cohort",
    values="retention_rate",
    title="Customer Retention by Cohort",
    x_label="Months Since First Purchase",
    y_label="Cohort (First Purchase Month)",
    color_scale="Purples",
    height=600
)

st.plotly_chart(fig, use_container_width=True)
```

---

## 🎯 Best Practices

### 1. **Consistent Spacing**
```python
# Use section headers to separate major areas
section("Revenue Analysis", icon="💰")

# Add KPIs at the top
kpi_row([...])

# Wrap charts in cards
card(title="Trend Chart", body_fn=render_chart)
```

### 2. **Loading States**
```python
with st.spinner("Processing..."):
    # Long operation
    result = process_data()

# Or use skeleton loader
skeleton_loader(lines=5)
```

### 3. **Responsive Layouts**
```python
# For mobile-friendly layouts
col1, col2 = st.columns([2, 1])  # 2:1 ratio

with col1:
    # Main content
    
with col2:
    # Sidebar content
```

### 4. **Error Handling**
```python
try:
    data = load_data()
    toast_success("Data loaded!")
except Exception as e:
    toast_error(f"Error: {str(e)}")
    empty_state(
        title="Failed to Load Data",
        description=str(e),
        cta_label="Retry",
        cta_callback=load_data
    )
```

### 5. **RTL Support**
```python
# All components automatically support RTL
# Just pass the language parameter

language = st.session_state.language  # 'en' or 'ar'

section(
    title="العملاء" if language == 'ar' else "Customers",
    language=language
)
```

---

## 🎨 Color Reference

```python
from app.ui.theme import DESIGN_TOKENS

colors = DESIGN_TOKENS["colors"]

# Primary colors
colors["primary"]        # #7C3AED (Purple)
colors["secondary"]      # #2563EB (Blue)

# Status colors
colors["success"]        # #10B981 (Green)
colors["warning"]        # #F59E0B (Orange)
colors["error"]          # #EF4444 (Red)
colors["info"]           # #3B82F6 (Blue)

# Neutral grays
colors["gray_100"]       # #F3F4F6 (Light)
colors["gray_500"]       # #6B7280 (Medium)
colors["gray_900"]       # #111827 (Dark)

# Gradients
colors["gradient_primary"]  # Purple → Blue
colors["gradient_success"]  # Green gradient
```

---

## 📱 Responsive Breakpoints

```python
# Use Streamlit columns for responsive layouts

# Desktop (3 columns)
if not is_mobile():
    col1, col2, col3 = st.columns(3)
    
# Mobile (1 column)
else:
    col1 = st.columns(1)
```

---

## ♿ Accessibility Tips

1. **Use semantic HTML**: Components use proper heading hierarchy
2. **Contrast ratios**: All text meets WCAG AA standard (4.5:1)
3. **Keyboard navigation**: All interactive elements are keyboard accessible
4. **ARIA labels**: Stepper and badges include proper ARIA attributes
5. **Focus indicators**: Visible focus outlines on all interactive elements

---

## 🚀 Performance Tips

1. **Lazy load heavy components**: Use `@st.cache_data` for expensive operations
2. **Minimize recompute**: Use session state to cache computed values
3. **Optimize charts**: Limit data points to ~1000 for smooth rendering
4. **Use skeleton loaders**: Show loading states instead of spinners

---

## 📚 Related Documentation

- `UI_REDESIGN_STATUS.md` - Implementation roadmap
- `app/ui/theme.py` - Complete design token reference
- `app/ui/components.py` - Component source code
- `app/ui/charts.py` - Chart helper functions

---

**Last Updated:** October 18, 2025
**Design System Version:** 2.0.0
