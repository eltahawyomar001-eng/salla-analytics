"""Geographic Analytics page - visualize revenue and customer distribution by location."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any

from app.ui.components import get_translator, format_currency, format_number
from app.analytics.geo import GeoAnalyzer


def render_geo_analytics_page():
    """Render the geographic analytics page."""
    language = st.session_state.language
    t = get_translator(language)
    
    # Check if data is loaded
    if not st.session_state.get('data_loaded', False):
        st.warning(t['errors']['no_data'])
        st.info("👆 " + ("Please upload data first" if language == 'en' else "يرجى تحميل البيانات أولاً"))
        return
    
    # Get cleaned dataframe
    df_clean = st.session_state.get('df_clean')
    
    if df_clean is None or df_clean.empty:
        st.error(t['errors']['no_analysis'])
        return
    
    # Initialize geo analyzer
    geo_analyzer = GeoAnalyzer(df_clean)
    
    # Check if location data is available
    location_summary = geo_analyzer.get_location_summary()
    
    if not location_summary.get('has_data', False):
        _show_no_location_data_message(t, language)
        return
    
    # Page header
    st.title("🗺️ " + t.get('geo_analytics', {}).get('title', 'Geographic Analytics'))
    st.markdown(t.get('geo_analytics', {}).get('description', 
        'Analyze revenue and customer distribution across different geographic locations'))
    
    # Show available location fields with coverage info
    available_fields = location_summary.get('available_fields', [])
    
    if not available_fields:
        _show_no_location_data_message(t, language)
        return
    
    # Display available location types
    with st.expander("📊 Available Location Data", expanded=False):
        for field_info in available_fields:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(field_info['field'].title(), field_info['unique_values'])
            with col2:
                st.metric("Coverage", f"{field_info['coverage_pct']}%")
            with col3:
                st.metric("Column", field_info['column'])
            with col4:
                st.metric("Non-null", format_number(field_info['non_null_count'], language, decimals=0))
    
    st.markdown("---")
    
    # Create tabs for each location type
    field_names = [field['field'].title() for field in available_fields]
    tabs = st.tabs([f"📍 {name}" for name in field_names])
    
    # Render each location type in its own tab
    for idx, (tab, field_info) in enumerate(zip(tabs, available_fields)):
        with tab:
            _render_location_analysis(
                geo_analyzer=geo_analyzer,
                location_type=field_info['field'],
                column_name=field_info['column'],
                t=t,
                language=language,
                tab_idx=idx
            )


def _render_location_analysis(
    geo_analyzer: GeoAnalyzer,
    location_type: str,
    column_name: str,
    t: Dict[str, Any],
    language: str,
    tab_idx: int
):
    """Render analysis for a specific location type."""
    
    # Get data
    geo_df = geo_analyzer.get_revenue_by_location(location_type, min_orders=1)
    
    if geo_df.empty:
        st.warning(f"⚠️ No data available for {location_type}")
        return
    
    # Get insights
    insights = geo_analyzer.get_geographic_insights(location_type)
    
    # Get currency from session state
    kpis = st.session_state.analysis_results.get('kpis', {})
    currency = kpis.get('currency')
    
    # === KEY METRICS ===
    st.markdown(f"### 📊 Key Metrics")
    
    cols = st.columns(4)
    
    with cols[0]:
        st.metric(
            label=f"📍 Total {location_type.title()}s",
            value=format_number(insights['total_locations'], language, decimals=0)
        )
    
    with cols[1]:
        top_loc = insights['top_location']
        st.metric(
            label=f"🏆 Top {location_type.title()}",
            value=top_loc['name'],
            delta=format_currency(top_loc['revenue'], currency, language)
        )
    
    with cols[2]:
        st.metric(
            label="📊 Revenue Concentration",
            value=f"{insights['concentration']['top_5_pct']}%",
            delta=f"Top 5 {location_type}s ({insights['concentration']['description']})"
        )
    
    with cols[3]:
        highest_aov = insights['highest_aov_location']
        st.metric(
            label="💰 Highest AOV",
            value=highest_aov['name'],
            delta=format_currency(highest_aov['aov'], currency, language)
        )
    
    st.markdown("---")
    
    # === INTERACTIVE MAP ===
    st.markdown(f"### 🗺️ Revenue Distribution Map")
    
    # Create map based on location type
    fig_map = _create_revenue_map(geo_df, location_type, geo_analyzer, currency)
    
    if fig_map:
        st.plotly_chart(fig_map, use_container_width=True, key=f"map_{tab_idx}")
    
    st.markdown("---")
    
    # === TOP LOCATIONS TABLE ===
    st.markdown(f"### 🏆 Top {location_type.title()}s by Revenue")
    
    # Display top 15 locations
    display_df = geo_df.head(15)[['location', 'revenue', 'orders', 'customers', 'avg_order_value', 'revenue_pct']].copy()
    display_df.columns = [
        location_type.title(), 
        'Revenue', 
        'Orders', 
        'Customers', 
        'Avg Order Value', 
        'Revenue %'
    ]
    
    # Format numeric columns
    display_df['Revenue'] = display_df['Revenue'].apply(lambda x: format_currency(x, currency, language))
    display_df['Avg Order Value'] = display_df['Avg Order Value'].apply(lambda x: format_currency(x, currency, language))
    display_df['Orders'] = display_df['Orders'].apply(lambda x: format_number(x, language, decimals=0))
    display_df['Customers'] = display_df['Customers'].apply(lambda x: format_number(x, language, decimals=0))
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("---")
    
    # === CHARTS ===
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"#### 💰 Revenue by {location_type.title()}")
        
        # Top 15 bar chart
        top_15 = geo_df.head(15)
        fig_revenue = px.bar(
            top_15,
            x='revenue',
            y='location',
            orientation='h',
            title=f'Top 15 {location_type.title()}s by Revenue',
            labels={'revenue': f'Revenue ({currency or "$"})', 'location': location_type.title()},
            color='revenue',
            color_continuous_scale='Blues',
            text='revenue'
        )
        fig_revenue.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        fig_revenue.update_layout(
            height=500,
            showlegend=False,
            yaxis={'categoryorder': 'total ascending'}
        )
        
        st.plotly_chart(fig_revenue, use_container_width=True, key=f"revenue_{tab_idx}")
    
    with col2:
        st.markdown(f"#### 👥 Customers by {location_type.title()}")
        
        # Customer distribution
        fig_customers = px.bar(
            top_15,
            x='customers',
            y='location',
            orientation='h',
            title=f'Top 15 {location_type.title()}s by Customers',
            labels={'customers': 'Customers', 'location': location_type.title()},
            color='customers',
            color_continuous_scale='Greens',
            text='customers'
        )
        fig_customers.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        fig_customers.update_layout(
            height=500,
            showlegend=False,
            yaxis={'categoryorder': 'total ascending'}
        )
        
        st.plotly_chart(fig_customers, use_container_width=True, key=f"customers_{tab_idx}")
    
    st.markdown("---")
    
    # === PERFORMANCE SCATTER ===
    st.markdown(f"#### 📈 Performance Matrix: Orders vs Average Order Value")
    
    # Scatter plot showing relationship between order volume and AOV
    fig_scatter = px.scatter(
        geo_df.head(20),
        x='orders',
        y='avg_order_value',
        size='revenue',
        text='location',
        title=f'{location_type.title()} Performance: Order Volume vs Average Order Value',
        labels={
            'orders': 'Number of Orders',
            'avg_order_value': f'Average Order Value ({currency or "$"})',
            'location': location_type.title()
        },
        color='revenue',
        color_continuous_scale='Viridis',
        hover_data={'revenue': ':,.2f', 'customers': True, 'orders': True, 'avg_order_value': ':,.2f'}
    )
    fig_scatter.update_traces(textposition='top center', textfont_size=9)
    fig_scatter.update_layout(height=500)
    
    st.plotly_chart(fig_scatter, use_container_width=True, key=f"scatter_{tab_idx}")
    
    st.markdown("---")
    
    # === DATA EXPORT ===
    st.markdown("### 📥 Export Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # CSV export
        csv_data = geo_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 Download as CSV",
            data=csv_data,
            file_name=f"{location_type}_revenue_data.csv",
            mime="text/csv",
            key=f"csv_{tab_idx}"
        )
    
    with col2:
        # Excel export
        from io import BytesIO
        buffer = BytesIO()
        geo_df.to_excel(buffer, index=False, engine='xlsxwriter')
        excel_data = buffer.getvalue()
        
        st.download_button(
            label="📥 Download as Excel",
            data=excel_data,
            file_name=f"{location_type}_revenue_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"excel_{tab_idx}"
        )


def _create_revenue_map(
    geo_df: pd.DataFrame,
    location_type: str,
    geo_analyzer: GeoAnalyzer,
    currency: str
) -> go.Figure:
    """Create an interactive map showing revenue distribution.
    
    Args:
        geo_df: GeoDataFrame with location and revenue data
        location_type: Type of location (city, state, country, etc.)
        geo_analyzer: GeoAnalyzer instance
        currency: Currency symbol/code
        
    Returns:
        Plotly Figure with map visualization
    """
    
    # For country-level data, use choropleth map
    if location_type == 'country':
        try:
            fig = px.choropleth(
                geo_df,
                locations='location',
                locationmode='country names',
                color='revenue',
                hover_name='location',
                hover_data={
                    'revenue': ':,.0f',
                    'orders': ':,',
                    'customers': ':,',
                    'avg_order_value': ':,.2f',
                    'revenue_pct': ':.1f'
                },
                title=f'Revenue by Country',
                color_continuous_scale='Blues',
                labels={'revenue': f'Revenue ({currency or "$"})'}
            )
            fig.update_geos(showcountries=True, showcoastlines=True, showland=True)
            fig.update_layout(height=600)
            return fig
        except Exception as e:
            st.warning(f"Could not create country map: {e}")
    
    # For other location types, create a bubble map
    # Note: This is a simplified representation since we don't have lat/lon
    # In production, you'd geocode the locations
    
    # Create a scatter geo map with estimated positions
    # For now, we'll create a simple bar chart representation on a map
    
    # Use density mapbox for city-level data if country is detected
    primary_country = geo_analyzer.get_country_for_map()
    
    # Create a table-style map as fallback
    # Show top 20 locations in a treemap instead
    top_20 = geo_df.head(20)
    
    fig = px.treemap(
        top_20,
        path=[px.Constant(f"All {location_type.title()}s"), 'location'],
        values='revenue',
        color='revenue',
        hover_data={
            'revenue': ':,.0f',
            'orders': ':,',
            'customers': ':,',
            'avg_order_value': ':,.2f'
        },
        color_continuous_scale='Blues',
        title=f'Revenue Distribution by {location_type.title()} (Treemap)'
    )
    fig.update_traces(textinfo="label+value+percent parent")
    fig.update_layout(height=600)
    
    return fig


def _show_no_location_data_message(t: Dict[str, Any], language: str):
    """Show helpful message when no location data is available."""
    
    st.warning("⚠️ " + t.get('geo_analytics', {}).get('no_location_data', 'No location data found'))
    
    if language == 'en':
        st.markdown("""
        ### Why is this page empty?
        
        Your data doesn't contain geographic location information (city, country, state, region, etc.).
        
        ### What you need:
        
        ✅ **Location columns** in your data export  
        ✅ **City, Country, State, or Region** information  
        
        ### What to do:
        
        1. **Export data with location fields** - Ensure your e-commerce platform export includes customer location data
        2. **Check export settings** - Look for address, city, state, or country fields in export options
        3. **Use alternative exports** - Try different export formats that include location information
        4. **Focus on other analyses** - Use Customer Segments, Cohorts, and Products pages for insights
        
        ---
        
        💡 **Tip:** We automatically detect location columns in multiple languages:
        - **English**: City, State, Country, Region, Province, County
        - **Arabic**: المدينة, الدولة, المنطقة, المحافظة
        - **German**: Stadt, Bundesland, Land
        - **And more...**
        """)
    else:
        st.markdown("""
        ### لماذا هذه الصفحة فارغة؟
        
        بياناتك لا تحتوي على معلومات الموقع الجغرافي (المدينة، الدولة، المنطقة، إلخ).
        
        ### ما تحتاجه:
        
        ✅ **أعمدة الموقع** في ملف التصدير  
        ✅ **معلومات المدينة أو الدولة أو المنطقة**  
        
        ### ما يجب فعله:
        
        1. **تصدير البيانات مع حقول الموقع** - تأكد من أن تصدير منصة التجارة الإلكترونية يتضمن بيانات موقع العميل
        2. **التحقق من إعدادات التصدير** - ابحث عن حقول العنوان أو المدينة أو المنطقة أو الدولة
        3. **استخدام تصديرات بديلة** - جرب صيغ تصدير مختلفة تتضمن معلومات الموقع
        4. **التركيز على التحليلات الأخرى** - استخدم صفحات شرائح العملاء والمجموعات والمنتجات
        
        ---
        
        💡 **نصيحة:** نكتشف تلقائياً أعمدة الموقع بعدة لغات:
        - **العربية**: المدينة، الدولة، المنطقة، المحافظة
        - **الإنجليزية**: City, State, Country, Region
        - **وأكثر...**
        """)
