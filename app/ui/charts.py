"""Centralized chart theming and helper functions for Plotly visualizations.

This module provides:
- Consistent Plotly theme configuration
- Helper functions for common chart types
- Responsive and accessible chart defaults
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Optional, Dict, Any, List


# Modern Plotly Theme Configuration
CHART_THEME = {
    "layout": {
        "font": {
            "family": "'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif",
            "size": 14,
            "color": "#374151"
        },
        "title": {
            "font": {
                "size": 20,
                "color": "#111827",
                "family": "'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif"
            },
            "x": 0.5,
            "xanchor": "center"
        },
        "plot_bgcolor": "#FFFFFF",
        "paper_bgcolor": "#FFFFFF",
        "colorway": [
            "#7C3AED",  # Primary purple
            "#2563EB",  # Secondary blue
            "#10B981",  # Success green
            "#F59E0B",  # Warning orange
            "#EF4444",  # Error red
            "#8B5CF6",  # Purple variant
            "#3B82F6",  # Blue variant
            "#14B8A6",  # Teal
        ],
        "margin": {
            "l": 60,
            "r": 40,
            "t": 80,
            "b": 60
        },
        "hovermode": "closest",
        "hoverlabel": {
            "bgcolor": "#FFFFFF",
            "bordercolor": "#E5E7EB",
            "font": {
                "family": "'Inter', 'Segoe UI', system-ui",
                "size": 13,
                "color": "#374151"
            }
        },
        "xaxis": {
            "gridcolor": "#F3F4F6",
            "linecolor": "#E5E7EB",
            "tickfont": {"size": 12, "color": "#6B7280"},
            "titlefont": {"size": 14, "color": "#374151"}
        },
        "yaxis": {
            "gridcolor": "#F3F4F6",
            "linecolor": "#E5E7EB",
            "tickfont": {"size": 12, "color": "#6B7280"},
            "titlefont": {"size": 14, "color": "#374151"}
        },
        "legend": {
            "bgcolor": "rgba(255, 255, 255, 0.8)",
            "bordercolor": "#E5E7EB",
            "borderwidth": 1,
            "font": {"size": 12, "color": "#374151"}
        }
    }
}


def apply_chart_theme(fig: go.Figure, title: str | None = None, height: int = 500) -> go.Figure:
    """Apply consistent theme to a Plotly figure.
    
    Args:
        fig: Plotly figure object
        title: Optional chart title
        height: Chart height in pixels
        
    Returns:
        Themed Plotly figure
    """
    fig.update_layout(
        **CHART_THEME["layout"],
        title=title,
        height=height,
        showlegend=True,
        template="plotly_white"
    )
    
    # Add subtle shadow effect via border
    fig.update_layout(
        margin=dict(l=60, r=40, t=80, b=60, pad=10)
    )
    
    return fig


def line_trend(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str | None = None,
    x_label: str | None = None,
    y_label: str | None = None,
    color: str | None = None,
    height: int = 500,
    show_markers: bool = True,
    smooth: bool = False
) -> go.Figure:
    """Create a modern line trend chart.
    
    Args:
        df: DataFrame containing the data
        x: Column name for x-axis
        y: Column name for y-axis
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label
        color: Column name for color grouping
        height: Chart height in pixels
        show_markers: Whether to show markers on line
        smooth: Whether to apply line smoothing
        
    Returns:
        Plotly figure object
    """
    if color:
        fig = px.line(
            df, x=x, y=y, color=color,
            title=title,
            labels={x: x_label or x, y: y_label or y},
            line_shape='spline' if smooth else 'linear',
            markers=show_markers
        )
    else:
        fig = px.line(
            df, x=x, y=y,
            title=title,
            labels={x: x_label or x, y: y_label or y},
            line_shape='spline' if smooth else 'linear',
            markers=show_markers
        )
    
    # Apply theme
    fig = apply_chart_theme(fig, title=title, height=height)
    
    # Enhance line appearance
    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=8, line=dict(width=2, color='white')) if show_markers else None
    )
    
    return fig


def bar_compare(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str | None = None,
    x_label: str | None = None,
    y_label: str | None = None,
    color: str | None = None,
    orientation: str = 'v',
    height: int = 500,
    show_values: bool = True
) -> go.Figure:
    """Create a modern bar comparison chart.
    
    Args:
        df: DataFrame containing the data
        x: Column name for x-axis
        y: Column name for y-axis
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label
        color: Column name for color grouping
        orientation: Bar orientation ('v' for vertical, 'h' for horizontal)
        height: Chart height in pixels
        show_values: Whether to show values on bars
        
    Returns:
        Plotly figure object
    """
    fig = px.bar(
        df, x=x, y=y, color=color,
        title=title,
        labels={x: x_label or x, y: y_label or y},
        orientation=orientation,
        text=y if show_values else None
    )
    
    # Apply theme
    fig = apply_chart_theme(fig, title=title, height=height)
    
    # Enhance bar appearance
    fig.update_traces(
        marker=dict(
            line=dict(width=0),
            opacity=0.9
        ),
        texttemplate='%{text:.2s}' if show_values else None,
        textposition='outside'
    )
    
    # Add rounded corners effect (simulated with opacity gradient)
    fig.update_traces(marker_pattern_shape="")
    
    return fig


def pie_distribution(
    df: pd.DataFrame,
    values: str,
    names: str,
    title: str | None = None,
    height: int = 500,
    hole: float = 0.4,
    show_legend: bool = True
) -> go.Figure:
    """Create a modern pie/donut chart.
    
    Args:
        df: DataFrame containing the data
        values: Column name for slice values
        names: Column name for slice names
        title: Chart title
        height: Chart height in pixels
        hole: Size of center hole (0 for pie, 0.4+ for donut)
        show_legend: Whether to show legend
        
    Returns:
        Plotly figure object
    """
    fig = px.pie(
        df, values=values, names=names,
        title=title,
        hole=hole
    )
    
    # Apply theme
    fig = apply_chart_theme(fig, title=title, height=height)
    
    # Enhance pie appearance
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        marker=dict(line=dict(color='white', width=3)),
        pull=[0.05 if i == 0 else 0 for i in range(len(df))]  # Pull out first slice
    )
    
    fig.update_layout(showlegend=show_legend)
    
    return fig


def cohort_heatmap(
    df: pd.DataFrame,
    x: str,
    y: str,
    values: str,
    title: str | None = None,
    x_label: str | None = None,
    y_label: str | None = None,
    height: int = 600,
    color_scale: str = "Purples"
) -> go.Figure:
    """Create a modern cohort heatmap.
    
    Args:
        df: DataFrame containing the data
        x: Column name for x-axis (cohort periods)
        y: Column name for y-axis (cohort groups)
        values: Column name for cell values
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label
        height: Chart height in pixels
        color_scale: Plotly color scale name
        
    Returns:
        Plotly figure object
    """
    # Pivot data for heatmap
    pivot_df = df.pivot(index=y, columns=x, values=values)
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_df.values,
        x=pivot_df.columns,
        y=pivot_df.index,
        colorscale=color_scale,
        text=pivot_df.values,
        texttemplate='%{text:.1f}%',
        textfont={"size": 11},
        hovertemplate='<b>%{y}</b><br>Period: %{x}<br>Value: %{z:.2f}%<extra></extra>',
        colorbar=dict(
            title="Retention %",
            thickness=15,
            len=0.7,
            tickfont=dict(size=11)
        )
    ))
    
    # Apply theme
    fig = apply_chart_theme(fig, title=title, height=height)
    
    # Update axes labels
    fig.update_xaxes(title_text=x_label or x)
    fig.update_yaxes(title_text=y_label or y)
    
    return fig


def scatter_plot(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str | None = None,
    x_label: str | None = None,
    y_label: str | None = None,
    color: str | None = None,
    size: str | None = None,
    height: int = 500,
    show_trendline: bool = False
) -> go.Figure:
    """Create a modern scatter plot.
    
    Args:
        df: DataFrame containing the data
        x: Column name for x-axis
        y: Column name for y-axis
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label
        color: Column name for color grouping
        size: Column name for bubble size
        height: Chart height in pixels
        show_trendline: Whether to show trendline
        
    Returns:
        Plotly figure object
    """
    fig = px.scatter(
        df, x=x, y=y, color=color, size=size,
        title=title,
        labels={x: x_label or x, y: y_label or y},
        trendline="ols" if show_trendline else None
    )
    
    # Apply theme
    fig = apply_chart_theme(fig, title=title, height=height)
    
    # Enhance scatter appearance
    fig.update_traces(
        marker=dict(
            line=dict(width=1, color='white'),
            opacity=0.7
        )
    )
    
    return fig


def area_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str | None = None,
    x_label: str | None = None,
    y_label: str | None = None,
    color: str | None = None,
    height: int = 500,
    stacked: bool = False
) -> go.Figure:
    """Create a modern area chart.
    
    Args:
        df: DataFrame containing the data
        x: Column name for x-axis
        y: Column name for y-axis
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label
        color: Column name for color grouping
        height: Chart height in pixels
        stacked: Whether to stack areas
        
    Returns:
        Plotly figure object
    """
    fig = px.area(
        df, x=x, y=y, color=color,
        title=title,
        labels={x: x_label or x, y: y_label or y}
    )
    
    # Apply theme
    fig = apply_chart_theme(fig, title=title, height=height)
    
    # Enhance area appearance
    fig.update_traces(
        fillcolor=None,
        opacity=0.6,
        line=dict(width=2)
    )
    
    if stacked:
        fig.update_layout(hovermode='x unified')
    
    return fig


def funnel_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str | None = None,
    height: int = 500,
    show_percentages: bool = True
) -> go.Figure:
    """Create a modern funnel chart.
    
    Args:
        df: DataFrame containing the data
        x: Column name for funnel values
        y: Column name for funnel stages
        title: Chart title
        height: Chart height in pixels
        show_percentages: Whether to show percentages
        
    Returns:
        Plotly figure object
    """
    fig = go.Figure(go.Funnel(
        y=df[y],
        x=df[x],
        textinfo="value+percent initial" if show_percentages else "value",
        marker=dict(
            color=CHART_THEME["layout"]["colorway"][:len(df)],
            line=dict(width=2, color="white")
        ),
        connector=dict(line=dict(color="#E5E7EB", width=2))
    ))
    
    # Apply theme
    fig = apply_chart_theme(fig, title=title, height=height)
    
    return fig


def gauge_chart(
    value: float,
    max_value: float = 100,
    title: str | None = None,
    height: int = 400,
    thresholds: Dict[str, float] | None = None
) -> go.Figure:
    """Create a modern gauge chart.
    
    Args:
        value: Current value
        max_value: Maximum value for gauge
        title: Chart title
        height: Chart height in pixels
        thresholds: Dictionary of threshold names and values
        
    Returns:
        Plotly figure object
    """
    if thresholds is None:
        thresholds = {
            "low": max_value * 0.33,
            "medium": max_value * 0.66,
            "high": max_value
        }
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 20}},
        delta={'reference': max_value * 0.5},
        gauge={
            'axis': {'range': [None, max_value], 'tickwidth': 1, 'tickcolor': "#6B7280"},
            'bar': {'color': "#7C3AED", 'thickness': 0.75},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#E5E7EB",
            'steps': [
                {'range': [0, thresholds["low"]], 'color': '#FEE2E2'},
                {'range': [thresholds["low"], thresholds["medium"]], 'color': '#FEF3C7'},
                {'range': [thresholds["medium"], max_value], 'color': '#D1FAE5'}
            ],
            'threshold': {
                'line': {'color': "#EF4444", 'width': 4},
                'thickness': 0.75,
                'value': max_value * 0.9
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor="white",
        font={'color': "#374151", 'family': "'Inter', 'Segoe UI', system-ui"},
        height=height
    )
    
    return fig


def create_metric_card_chart(
    value: float,
    title: str,
    prefix: str = "",
    suffix: str = "",
    delta: float | None = None,
    delta_reference: str = "vs last period"
) -> Dict[str, Any]:
    """Create data for a metric card display (returns dict for Streamlit st.metric).
    
    Args:
        value: Metric value
        title: Metric title
        prefix: Value prefix (e.g., "$")
        suffix: Value suffix (e.g., "%")
        delta: Change value
        delta_reference: Description of delta reference
        
    Returns:
        Dictionary with metric data
    """
    return {
        "label": title,
        "value": f"{prefix}{value:,.2f}{suffix}",
        "delta": f"{delta:+.2f}{suffix}" if delta is not None else None,
        "delta_color": "normal" if delta is None else ("inverse" if delta < 0 else "normal"),
        "help": delta_reference if delta is not None else None
    }
