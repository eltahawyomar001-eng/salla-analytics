"""Financial Insights & Recommendations page."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from app.ui.components import get_translator, format_currency, format_number, format_percentage
from app.analytics.financial_insights import FinancialInsightsEngine


def render_insights_page():
    """Render the financial insights and actionable recommendations page."""
    language = st.session_state.language
    t = get_translator(language)
    
    if not st.session_state.get('data_loaded', False):
        st.warning(t['errors']['no_data'])
        return
    
    # Get currency from KPIs for formatting
    kpis = st.session_state.analysis_results.get('kpis', {})
    currency = kpis.get('currency')
    currency_display = currency if currency else "Currency"
    
    st.title("💰 Financial Insights & Action Plan")
    
    st.markdown("""
    ### Your Roadmap to Revenue Growth
    
    This page provides **specific, actionable recommendations** with financial projections. 
    Each recommendation includes:
    - 💵 **Expected Revenue Impact**
    - 📊 **Required Investment** 
    - 📈 **Projected ROI**
    - ⏱️ **Implementation Timeline**
    - ✅ **Quick Win Actions**
    """)
    
    # Initialize insights engine
    try:
        insights_engine = FinancialInsightsEngine(
            df=st.session_state.df_clean,
            analysis_results=st.session_state.analysis_results
        )
    except Exception as e:
        st.error(f"Error initializing insights engine: {str(e)}")
        return
    
    # Executive Summary
    st.markdown("---")
    st.markdown("## 📊 Executive Summary")
    
    exec_recommendations = insights_engine.generate_executive_recommendations()
    
    # Critical metrics cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Customers at Risk",
            format_number(exec_recommendations['critical_metrics']['at_risk_customers'], language, decimals=0),
            delta=f"-{format_percentage(exec_recommendations['critical_metrics']['at_risk_customers'] / insights_engine.kpis.get('customer_metrics', {}).get('total_customers', 1), decimals=0)}"
        )
    
    with col2:
        st.metric(
            "Revenue at Risk",
            format_currency(exec_recommendations['critical_metrics']['revenue_at_risk'], language=language),
            delta="Needs Action",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            "Recovery Investment",
            format_currency(exec_recommendations['critical_metrics']['recovery_investment'], language=language)
        )
    
    with col4:
        roi = exec_recommendations['financial_summary']['projected_roi']
        st.metric(
            "Expected ROI",
            f"{roi:.0f}%",
            delta="High Return"
        )
    
    # Key Decisions
    st.markdown("### 🎯 Key Decisions Required")
    for idx, decision in enumerate(exec_recommendations['key_decisions'], 1):
        st.info(f"**{idx}.** {decision}")
    
    # Top 3 Priorities
    st.markdown("---")
    st.markdown("## 🏆 Top 3 Priority Segments")
    st.markdown("*Focus on these for maximum impact*")
    
    for priority in exec_recommendations['top_3_priorities']:
        with st.expander(f"#{priority['rank']} - {priority['segment']} ({format_number(priority['customers'], language, decimals=0)} customers) - {priority['quadrant']}", expanded=priority['rank'] == 1):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Potential Revenue Gain",
                    format_currency(priority['potential_revenue'], language=language)
                )
            
            with col2:
                st.metric(
                    "ROI",
                    f"{priority['roi_percentage']:.0f}%"
                )
            
            with col3:
                st.metric(
                    "Customers",
                    format_number(priority['customers'], language, decimals=0)
                )
            
            # Get detailed segment opportunity
            opportunities = insights_engine.calculate_segment_opportunities()
            opp = opportunities.get(priority['segment'], {})
            
            if opp:
                st.markdown("#### 📈 Revenue Scenarios")
                
                scenario_df = pd.DataFrame([
                    {
                        'Scenario': 'Retention Boost',
                        'Action': opp['scenarios']['retention']['action'],
                        'Impact': format_currency(opp['scenarios']['retention']['revenue_gain'], language=language),
                        'Customers': opp['scenarios']['retention']['customers_to_retain']
                    },
                    {
                        'Scenario': 'Frequency Boost',
                        'Action': opp['scenarios']['frequency']['action'],
                        'Impact': format_currency(opp['scenarios']['frequency']['revenue_gain'], language=language),
                        'Orders': opp['scenarios']['frequency']['additional_orders']
                    },
                    {
                        'Scenario': 'AOV Boost',
                        'Action': opp['scenarios']['aov']['action'],
                        'Impact': format_currency(opp['scenarios']['aov']['revenue_gain'], language=language),
                        'Increase': f"{opp['scenarios']['aov']['aov_increase_target']:.0f}%"
                    }
                ])
                
                st.dataframe(scenario_df, use_container_width=True, hide_index=True)
                
                # Quick Wins
                st.markdown("#### ⚡ Quick Win Actions (Start Today)")
                
                quick_wins = opp.get('quick_wins', [])
                for qw in quick_wins[:5]:
                    st.markdown(f"""
                    **{qw['action']}**
                    - ⏱️ Timeline: {qw['timeline']}
                    - 💰 Cost: {qw['cost']}
                    - 📊 Impact: {qw['impact']}
                    """)
                
                # Implementation Timeline
                timeline = opp.get('timeline', {})
                if timeline:
                    st.markdown("#### 📅 Implementation Timeline")
                    
                    timeline_df = pd.DataFrame([
                        {'Phase': 'Immediate', 'Action': timeline.get('immediate', 'N/A')},
                        {'Phase': 'Week 1', 'Action': timeline.get('week_1', 'N/A')},
                        {'Phase': 'Week 2', 'Action': timeline.get('week_2', 'N/A')},
                        {'Phase': 'Month 1', 'Action': timeline.get('month_1', 'N/A')},
                    ])
                    
                    st.table(timeline_df)
                    
                    st.success(f"**Expected Results:** {timeline.get('expected_results', 'Within 30-60 days')}")
    
    # Financial Summary
    st.markdown("---")
    st.markdown("## 💼 Financial Summary")
    
    fin_summary = exec_recommendations['financial_summary']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Investment Required")
        st.metric(
            "Total Investment",
            format_currency(fin_summary['required_investment'], language=language)
        )
        
        st.metric(
            "Payback Period",
            f"{fin_summary['payback_period_months']:.1f} months"
        )
    
    with col2:
        st.markdown("### Expected Returns")
        st.metric(
            "Total Opportunity",
            format_currency(fin_summary['total_opportunity'], language=language)
        )
        
        st.metric(
            "ROI",
            f"{fin_summary['projected_roi']:.0f}%"
        )
    
    # Revenue Scenarios
    st.markdown("---")
    st.markdown("## 📊 Revenue Projections")
    
    scenarios = insights_engine.project_revenue_scenarios()
    
    scenario_data = []
    for scenario_name, scenario_info in scenarios['scenarios'].items():
        scenario_data.append({
            'Scenario': scenario_name.replace('_', ' ').title(),
            'Growth Rate': f"{scenario_info['growth_rate']*100:+.0f}%",
            'Projected Revenue': scenario_info['projected_revenue'],
            'Change': scenario_info['change'],
            'Description': scenario_info['description']
        })
    
    scenario_df = pd.DataFrame(scenario_data)
    
    # Create visualization
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=scenario_df['Scenario'],
        y=scenario_df['Projected Revenue'],
        text=[format_currency(v, language=language) for v in scenario_df['Projected Revenue']],
        textposition='auto',
        marker_color=['red', 'orange', 'green']
    ))
    
    fig.update_layout(
        title="Revenue Scenarios Comparison",
        xaxis_title="Scenario",
        yaxis_title=f"Projected Annual Revenue ({currency_display})",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(scenario_df[['Scenario', 'Growth Rate', 'Description']], use_container_width=True, hide_index=True)
    
    st.info(f"**Recommended Scenario:** {scenarios['recommended_scenario'].replace('_', ' ').title()}")
    
    # Priority Action Matrix
    st.markdown("---")
    st.markdown("## 🎯 Priority Action Matrix")
    st.markdown("*Eisenhower Matrix: Prioritize by Impact vs Effort*")
    
    priority_matrix = insights_engine.get_priority_action_matrix()
    
    matrix_df = pd.DataFrame(priority_matrix)
    
    # Create scatter plot
    fig = px.scatter(
        matrix_df,
        x='effort_level',
        y='impact_score',
        size='potential_revenue',
        color='quadrant',
        hover_data=['segment', 'customer_count', 'roi'],
        text='segment',
        color_discrete_map={
            'DO FIRST': 'green',
            'SCHEDULE': 'orange',
            'DELEGATE': 'blue',
            'ELIMINATE': 'red'
        },
        title="Action Priority Matrix"
    )
    
    fig.update_traces(textposition='top center')
    fig.update_layout(height=500)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Matrix table
    display_matrix = matrix_df[['segment', 'quadrant', 'customer_count', 'potential_revenue', 'roi', 'effort_level']].copy()
    display_matrix['potential_revenue'] = display_matrix['potential_revenue'].apply(lambda x: format_currency(x, language=language))
    display_matrix['roi'] = display_matrix['roi'].apply(lambda x: f"{x:.0f}%")
    display_matrix.columns = ['Segment', 'Priority', 'Customers', 'Potential Revenue', 'ROI', 'Effort']
    
    st.dataframe(display_matrix, use_container_width=True, hide_index=True)
    
    # Churn Risk Analysis
    st.markdown("---")
    st.markdown("## ⚠️ Churn Risk Analysis")
    
    churn_risk = insights_engine.calculate_churn_risk()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "High Risk Customers",
            format_number(churn_risk['high_risk_customers'], language, decimals=0),
            delta=f"-{format_currency(churn_risk['high_risk_annual_revenue'], language=language)}",
            delta_color="inverse"
        )
    
    with col2:
        st.metric(
            "Medium Risk Customers",
            format_number(churn_risk['medium_risk_customers'], language, decimals=0),
            delta=f"-{format_currency(churn_risk['medium_risk_annual_revenue'], language=language)}",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            "Potential Loss",
            format_currency(churn_risk['potential_annual_loss'], language=language),
            delta="Without Action",
            delta_color="inverse"
        )
    
    st.warning(f"""
    **⚠️ URGENT:** You have **{format_number(churn_risk['total_at_risk'], language, decimals=0)} customers at risk** 
    representing **{format_currency(churn_risk['potential_annual_loss'], language=language)}** in potential lost revenue.
    
    **Investment needed to prevent this:** {format_currency(churn_risk['recovery_cost'], language=language)}
    
    **Net value at stake:** {format_currency(churn_risk['net_value_at_risk'], language=language)}
    """)
    
    # 90-Day Action Plan
    st.markdown("---")
    st.markdown("## 📅 Your 90-Day Action Plan")
    
    action_plan = exec_recommendations['recommended_action_plan']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📍 Days 1-30")
        for action in action_plan['days_1_30']:
            st.markdown(f"- {action}")
    
    with col2:
        st.markdown("### 📍 Days 31-60")
        for action in action_plan['days_31_60']:
            st.markdown(f"- {action}")
    
    with col3:
        st.markdown("### 📍 Days 61-90")
        for action in action_plan['days_61_90']:
            st.markdown(f"- {action}")
    
    # Download Action Plan
    st.markdown("---")
    st.markdown("## 📥 Download Your Action Plan")
    
    if st.button("📄 Generate Detailed Action Plan (PDF)", type="primary"):
        st.info("PDF generation will be implemented. For now, screenshot this page or use the Excel export from Summary page.")
    
    # Final CTA
    st.markdown("---")
    st.success("""
    ### 🚀 Ready to Take Action?
    
    **Next Steps:**
    1. Review the top 3 priority segments above
    2. Start with Quick Win actions (can be done today!)
    3. Allocate budget for the recommended investment
    4. Set up tracking to measure results
    5. Re-run this analysis in 30 days to measure progress
    
    **Remember:** Every day you delay costs you potential revenue. Start with segment #1 TODAY!
    """)
