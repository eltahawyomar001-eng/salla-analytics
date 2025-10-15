"""Executive summary page showing key metrics."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any

from app.ui.components import (
    get_translator, format_number, format_currency, 
    format_percentage, show_metric_card
)
from app.utils.mobile import (
    is_mobile, get_responsive_columns, mobile_friendly_chart_config
)

def render_summary_page():
    """Render the executive summary page."""
    language = st.session_state.language
    t = get_translator(language)
    
    # Debug: Show session state status
    with st.expander("🔧 Debug: Session State", expanded=False):
        st.write(f"**data_loaded**: {st.session_state.get('data_loaded', 'NOT SET')}")
        st.write(f"**analysis_results keys**: {list(st.session_state.get('analysis_results', {}).keys())}")
        st.write(f"**df_clean exists**: {'df_clean' in st.session_state}")
        st.write(f"**current_file**: {st.session_state.get('current_file', 'NOT SET')}")
    
    if not st.session_state.get('data_loaded', False):
        st.warning(t['errors']['no_data'])
        st.info("👆 Please go to the Upload page and upload your data file first.")
        return
    
    st.title(t['summary']['title'])
    st.markdown(t['summary']['description'])
    
    # Add helpful explanation
    st.info("💡 **Quick Guide:** This page shows your store's overall performance. Scroll down to see revenue trends, customer distribution, and download a complete Excel report with all analysis.")
    
    kpis = st.session_state.analysis_results.get('kpis', {})
    
    if not kpis:
        st.error(t['errors']['no_analysis'])
        return
    
    # Debug: Show data that was analyzed
    if 'df_clean' in st.session_state:
        df_clean = st.session_state.df_clean
        with st.expander("📊 Data Details", expanded=False):
            # Get currency from KPIs
            currency = kpis.get('currency')
            currency_str = f"{currency} " if currency else ""
            
            st.write(f"**Total Rows Analyzed**: {len(df_clean):,}")
            st.write(f"**Date Range**: {df_clean['order_date'].min()} to {df_clean['order_date'].max()}")
            st.write(f"**Unique Customers**: {df_clean['customer_id'].nunique():,}")
            st.write(f"**Unique Orders**: {df_clean['order_id'].nunique():,}")
            st.write(f"**Total Revenue**: {currency_str}{df_clean['order_total'].sum():,.2f}")
    
    # Key metrics row
    st.markdown(f"## {t['summary']['key_metrics']}")
    
    # Get currency from KPIs for formatting
    currency = kpis.get('currency')
    
    # Responsive columns: 4 on desktop, 2 on tablet, 1 on mobile
    num_cols = get_responsive_columns(desktop_cols=4, tablet_cols=2, mobile_cols=1)
    cols = st.columns(num_cols)
    
    # Metrics data
    metrics_data = [
        {
            'label': t['summary']['total_revenue'],
            'value': format_currency(kpis.get('revenue_metrics', {}).get('total_revenue', 0), currency=currency, language=language)
        },
        {
            'label': t['summary']['total_orders'],
            'value': format_number(kpis.get('order_metrics', {}).get('total_orders', 0), language, decimals=0)
        },
        {
            'label': t['summary']['total_customers'],
            'value': format_number(kpis.get('customer_metrics', {}).get('total_customers', 0), language, decimals=0)
        },
        {
            'label': t['summary']['avg_order_value'],
            'value': format_currency(kpis.get('order_metrics', {}).get('average_order_value', 0), currency=currency, language=language)
        }
    ]
    
    # Display metrics in responsive columns
    for idx, metric in enumerate(metrics_data):
        col_idx = idx % num_cols
        with cols[col_idx]:
            show_metric_card(
                label=metric['label'],
                value=metric['value'],
                language=language
            )
    
    # Secondary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        repeat_rate = kpis.get('customer_metrics', {}).get('repeat_purchase_rate', 0) * 100
        show_metric_card(
            label=t['summary']['repeat_rate'],
            value=format_percentage(repeat_rate, language),
            language=language
        )
    
    with col2:
        avg_ltv = kpis.get('customer_metrics', {}).get('avg_customer_ltv', 0)
        show_metric_card(
            label=t['summary']['avg_ltv'],
            value=format_currency(avg_ltv, currency=currency, language=language),
            language=language
        )
    
    with col3:
        new_customers = kpis.get('customer_metrics', {}).get('new_customers', 0)
        show_metric_card(
            label=t['summary']['new_customers'],
            value=format_number(new_customers, language, decimals=0),
            language=language
        )
    
    with col4:
        returning_customers = kpis.get('customer_metrics', {}).get('returning_customers', 0)
        show_metric_card(
            label=t['summary']['returning_customers'],
            value=format_number(returning_customers, language, decimals=0),
            language=language
        )
    
    # Revenue trends chart
    st.markdown(f"## {t['summary']['revenue_trends']}")
    
    trend_data = kpis.get('trend_metrics', {}).get('monthly_trends', {})
    
    if trend_data:
        # Convert dict to dataframe
        df_trends = pd.DataFrame.from_dict(trend_data, orient='index')
        df_trends.index.name = 'period'
        df_trends = df_trends.reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_trends['period'],
            y=df_trends['revenue'],
            mode='lines+markers',
            name=t['summary']['revenue'],
            line=dict(color='#2E8B57', width=3)
        ))
        
        fig.update_layout(
            xaxis_title=t['summary']['month'],
            yaxis_title=t['summary']['revenue'],
            hovermode='x unified',
            height=300 if is_mobile() else 400
        )
        
        st.plotly_chart(fig, use_container_width=True, config=mobile_friendly_chart_config())
    
    # Distribution charts - responsive layout
    num_chart_cols = get_responsive_columns(desktop_cols=2, tablet_cols=1, mobile_cols=1)
    col1, col2 = st.columns(num_chart_cols) if num_chart_cols == 2 else (st.container(), st.container())
    
    with col1:
        st.markdown(f"### {t['summary']['customer_distribution']}")
        
        customer_metrics = kpis.get('customer_metrics', {})
        distribution_data = {
            t['summary']['new_customers']: customer_metrics.get('new_customers', 0),
            t['summary']['returning_customers']: customer_metrics.get('returning_customers', 0)
        }
        
        fig = px.pie(
            values=list(distribution_data.values()),
            names=list(distribution_data.keys()),
            color_discrete_sequence=['#4CAF50', '#2196F3']
        )
        fig.update_layout(height=250 if is_mobile() else 300)
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=250 if is_mobile() else 350)
        
        st.plotly_chart(fig, use_container_width=True, config=mobile_friendly_chart_config())
    
    with col2:
        st.markdown(f"### {t['summary']['revenue_distribution']}")
        
        revenue_dist = kpis.get('revenue_metrics', {}).get('revenue_distribution', {})
        
        if revenue_dist:
            df_dist = pd.DataFrame({
                'Percentile': list(revenue_dist.keys()),
                'Value': list(revenue_dist.values())
            })
            
            fig = px.bar(
                df_dist,
                x='Percentile',
                y='Value',
                color='Value',
                color_continuous_scale='Greens'
            )
            
            fig.update_layout(height=250 if is_mobile() else 350, showlegend=False)
            
            st.plotly_chart(fig, use_container_width=True, config=mobile_friendly_chart_config())
    
    # Export button
    st.markdown("---")
    st.markdown(f"## {t['export'].get('title', 'Export Report')}")
    
    if st.button(t['export'].get('download_excel', 'Download Excel Report'), type="primary"):
        try:
            from app.export.workbook import ExcelReportGenerator
            
            with st.spinner(t['export'].get('generating', 'Generating report...')):
                generator = ExcelReportGenerator(language=language)
                excel_file = generator.generate_report(
                    df_clean=st.session_state.df_clean,
                    analysis_results=st.session_state.analysis_results,
                    validation_report=st.session_state.get('validation_report', {}),
                    translations=t
                )
                
                # Generate filename safely
                df_clean = st.session_state.df_clean
                if isinstance(df_clean, pd.DataFrame) and len(df_clean) > 0 and 'order_date' in df_clean.columns:
                    date_str = df_clean['order_date'].max().strftime('%Y%m%d')
                else:
                    date_str = 'latest'
                
                st.download_button(
                    label=t['export'].get('download_button', 'Click to Download'),
                    data=excel_file,
                    file_name=f"Salla_Analysis_Report_{language}_{date_str}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                st.success(t['export'].get('success', 'Report generated successfully!'))
        
        except Exception as e:
            st.error(f"{t['errors'].get('export_error', 'Export error')}: {str(e)}")