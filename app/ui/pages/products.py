"""Products analysis page."""

import streamlit as st
import pandas as pd
import plotly.express as px

from app.ui.components import get_translator, format_currency, format_number

def render_products_page():
    """Render the products analysis page."""
    language = st.session_state.language
    t = get_translator(language)
    
    if not st.session_state.get('data_loaded', False):
        st.warning(t['errors']['no_data'])
        return
    
    st.title(t['navigation']['products'])
    
    # Add explanation
    if 'products' in t and 'explanation' in t['products']:
        st.info(t['products']['explanation'])
    
    product_results = st.session_state.analysis_results.get('products', {})
    
    # Get currency from KPIs for formatting
    kpis = st.session_state.analysis_results.get('kpis', {})
    currency = kpis.get('currency')
    currency_str = f"{currency} " if currency else ""
    
    if not product_results:
        st.warning(t['products'].get('no_product_data', t['errors']['no_analysis']))
        return
    
    # Top products
    st.markdown(f"## {t['products']['top_products']}")
    
    top_products = product_results.get('top_products_by_revenue', [])
    
    if top_products and len(top_products) > 0:
        df_products = pd.DataFrame(top_products[:10])
        
        # Show revenue chart
        fig = px.bar(
            df_products,
            x='revenue',
            y='product_name',
            orientation='h',
            color='revenue',
            color_continuous_scale='Greens',
            labels={'revenue': t['products']['revenue'], 'product_name': t['products']['product_name']},
            title=t['products']['top_products']
        )
        
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            height=500,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show data table with more details
        st.markdown("### Product Performance Details")
        display_df = df_products.copy()
        display_df['revenue'] = display_df['revenue'].apply(lambda x: f"{currency_str}{x:,.2f}")
        if 'quantity' in display_df.columns:
            display_df['quantity'] = display_df['quantity'].apply(lambda x: f"{int(x):,}")
        if 'customers' in display_df.columns:
            display_df['customers'] = display_df['customers'].apply(lambda x: f"{int(x):,}")
        st.dataframe(display_df, use_container_width=True)
    else:
        st.warning("No product data available to display.")