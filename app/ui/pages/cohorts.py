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
    
    if not cohort_results or not isinstance(cohort_results, dict):
        st.warning(t['cohorts'].get('no_cohort_data', t['errors']['no_analysis']))
        return
    
    # Retention heatmap
    st.markdown(f"## {t['cohorts']['retention_matrix']}")
    
    # Get retention matrix - it's stored as a dict, need to convert back to DataFrame
    retention_matrix_dict = cohort_results.get('retention_matrix', {})
    
    # Check if we have cohort data
    if retention_matrix_dict and isinstance(retention_matrix_dict, dict):
        # Convert dict back to DataFrame
        retention_matrix = pd.DataFrame.from_dict(retention_matrix_dict)
        
        if not retention_matrix.empty:
            # Convert Period index/columns to strings for JSON serialization
            x_labels = [str(col) for col in retention_matrix.columns]
            y_labels = [str(idx) for idx in retention_matrix.index]
            
            fig = go.Figure(data=go.Heatmap(
                z=retention_matrix.values * 100,
                x=x_labels,
                y=y_labels,
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
            
            # Show cohort summary
            st.markdown("---")
            st.markdown(f"## {t['cohorts'].get('summary', 'Cohort Summary')}")
            
            analysis_summary = cohort_results.get('analysis_summary', {})
            if analysis_summary:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Cohorts", analysis_summary.get('total_cohorts', 0))
                
                with col2:
                    avg_retention = analysis_summary.get('average_retention', 0) * 100
                    st.metric("Avg Retention", f"{avg_retention:.1f}%")
                
                with col3:
                    best_cohort = analysis_summary.get('best_performing_cohort', 'N/A')
                    st.metric("Best Cohort", str(best_cohort))
        else:
            # Show warning message
            _show_insufficient_data_message(t)
    else:
        # Show warning message
        _show_insufficient_data_message(t)


def _show_insufficient_data_message(t):
    """Show message when cohort data is insufficient."""
    st.warning("⚠️ **Insufficient data for cohort analysis**")
    
    st.markdown("""
    ### Why is this page empty?
    
    Cohort analysis requires customers who have made **repeat purchases** over multiple time periods.
    
    **Your current data shows:**
    - Not enough customers with repeat purchases
    - Or purchases are concentrated in a single time period
    - Or insufficient time range (need at least 2-3 months)
    
    ### What you need for cohort analysis:
    
    ✅ **At least 2-3 months of order data**  
    ✅ **Customers who purchased multiple times**  
    ✅ **Spread across different months**
    
    ### What to do:
    
    1. **Upload more historical data** - Include 3-6 months of orders
    2. **Wait and collect more data** - Come back when you have repeat customers
    3. **Focus on other pages** - Check Customer Segments (RFM) and Products pages for insights
    
    ---
    
    💡 **Tip:** Once you have customers making repeat purchases, cohort analysis will show you:
    - How many customers come back each month
    - Which cohorts have the best retention
    - When customers typically make their second purchase
    """)
    
    # Show what data we do have
    df_clean = st.session_state.get('df_clean')
    if df_clean is not None and not df_clean.empty:
        st.markdown("### 📊 Your Current Data:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_customers = df_clean['customer_id'].nunique()
            st.metric("Total Customers", f"{total_customers:,}")
        
        with col2:
            total_orders = len(df_clean)
            st.metric("Total Orders", f"{total_orders:,}")
        
        with col3:
            date_range_months = (df_clean['order_date'].max() - df_clean['order_date'].min()).days / 30
            st.metric("Date Range", f"{date_range_months:.1f} months")
        
        # Check repeat purchase rate
        customer_order_counts = df_clean.groupby('customer_id')['order_id'].nunique()
        repeat_customers = (customer_order_counts > 1).sum()
        repeat_rate = (repeat_customers / total_customers * 100) if total_customers > 0 else 0
        
        st.markdown(f"""
        **Repeat Purchase Analysis:**
        - Customers with 2+ orders: **{repeat_customers:,}** ({repeat_rate:.1f}%)
        - Single-purchase customers: **{total_customers - repeat_customers:,}**
        
        💡 You need at least **100 repeat customers** spread across **2+ months** for meaningful cohort analysis.
        """)