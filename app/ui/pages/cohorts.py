"""Cohort analysis page."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from app.ui.components import get_translator, format_percentage

def render_cohorts_page():
    """Render the cohort analysis page."""
    language = st.session_state.language
    t = get_translator(language)
    
    if not st.session_state.get('data_loaded', False):
        st.warning(t['errors']['no_data'])
        return
    
    st.title(t['navigation']['cohorts'])
    
    # Add explanation
    if 'cohorts' in t and 'explanation' in t['cohorts']:
        st.info(t['cohorts']['explanation'])
    
    cohort_results = st.session_state.analysis_results.get('cohorts', {})
    
    if not cohort_results:
        st.warning(t['cohorts'].get('no_cohort_data', t['errors']['no_analysis']))
        return
    
    # Retention heatmap
    st.markdown(f"## {t['cohorts']['retention_matrix']}")
    
    retention_matrix = cohort_results.get('retention_matrix', pd.DataFrame())
    
    if isinstance(retention_matrix, pd.DataFrame) and not retention_matrix.empty:
        fig = go.Figure(data=go.Heatmap(
            z=retention_matrix.values * 100,
            x=retention_matrix.columns.tolist(),
            y=retention_matrix.index.tolist(),
            colorscale='Blues',
            text=retention_matrix.values * 100,
            texttemplate='%{text:.1f}%',
            textfont={"size": 10}
        ))
        
        fig.update_layout(
            xaxis_title=t['cohorts']['period'],
            yaxis_title=t['cohorts']['cohort'],
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)