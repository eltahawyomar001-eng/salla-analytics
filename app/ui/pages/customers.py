"""Customers and RFM analysis page."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from app.ui.components import (
    get_translator, format_number, format_currency,
    create_segment_card
)

def render_customers_page():
    """Render the customers and RFM analysis page."""
    language = st.session_state.language
    t = get_translator(language)
    
    if not st.session_state.get('data_loaded', False):
        st.warning(t['errors']['no_data'])
        return
    
    st.title(t['customers']['title'])
    st.markdown(t['customers']['rfm_explanation'])
    
    # Add explanation box
    if 'segment_explanation' in t['customers']:
        st.info(t['customers']['segment_explanation'])
    
    rfm_results = st.session_state.analysis_results.get('rfm', {})
    
    if not isinstance(rfm_results, dict) or not rfm_results:
        st.error(t['errors']['no_analysis'])
        return
    
    # Segment summary
    st.markdown(f"## {t['customers']['segment_overview']}")
    
    segment_summary = rfm_results.get('segment_summary', {})
    
    # Display top 6 segments
    for segment_name, segment_data in list(segment_summary.items())[:6]:
        create_segment_card(segment_name, segment_data, t, language)
    
    # RFM heatmap
    st.markdown(f"## {t['customers']['rfm_heatmap']}")
    
    heatmap_data = rfm_results.get('heatmap_data', {})
    
    # Debug: Show what keys are available
    with st.expander("🔍 Debug: Heatmap Data Structure", expanded=False):
        st.write("Available keys:", list(heatmap_data.keys()) if heatmap_data else "No heatmap_data")
        if heatmap_data:
            st.write("value_matrix shape:", len(heatmap_data.get('value_matrix', [])))
            st.write("r_labels:", heatmap_data.get('r_labels', []))
            st.write("f_labels:", heatmap_data.get('f_labels', []))
    
    if heatmap_data and heatmap_data.get('value_matrix'):
        # Use correct key names from RFM analyzer
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.get('value_matrix', []),  # Fixed: was 'values'
            x=heatmap_data.get('r_labels', []),       # Fixed: was 'x_labels'
            y=heatmap_data.get('f_labels', []),       # Fixed: was 'y_labels'
            colorscale='Greens',
            text=heatmap_data.get('count_matrix', []),  # Show customer counts
            texttemplate='%{text:.0f} customers',
            hovertemplate='Recency: %{y}<br>Frequency: %{x}<br>Avg LTV: %{z:,.2f}<br>Customers: %{text}<extra></extra>'
        ))
        
        fig.update_layout(
            xaxis_title='Recency Score (R)',
            yaxis_title='Frequency Score (F)',
            height=600,
            title='RFM Heatmap: Average Customer Lifetime Value'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ No heatmap data available. This could mean insufficient customer data for heatmap generation.")