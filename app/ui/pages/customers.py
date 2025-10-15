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
    
    if heatmap_data:
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.get('values', []),
            x=heatmap_data.get('x_labels', []),
            y=heatmap_data.get('y_labels', []),
            colorscale='Greens'
        ))
        
        fig.update_layout(
            xaxis_title='Frequency',
            yaxis_title='Recency',
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)