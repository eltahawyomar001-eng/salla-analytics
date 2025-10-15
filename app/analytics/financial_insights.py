"""Financial insights and actionable recommendations module."""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
from datetime import datetime, timedelta


class FinancialInsightsEngine:
    """Generate actionable financial insights and recommendations."""
    
    def __init__(self, df: pd.DataFrame, analysis_results: Dict[str, Any]):
        """Initialize with cleaned data and analysis results."""
        self.df = df
        self.analysis_results = analysis_results
        self.kpis = analysis_results.get('kpis', {})
        self.rfm_results = analysis_results.get('rfm', {})
        
    def calculate_segment_opportunities(self) -> Dict[str, Any]:
        """Calculate revenue opportunities for each segment."""
        segment_summary = self.rfm_results.get('segment_summary', {})
        
        opportunities = {}
        total_customers = sum(seg.get('customer_count', 0) for seg in segment_summary.values())
        
        for segment_name, segment_data in segment_summary.items():
            customer_count = segment_data.get('customer_count', 0)
            avg_revenue = segment_data.get('avg_revenue_per_customer', 0)
            avg_frequency = segment_data.get('avg_frequency', 1)
            
            # Calculate opportunity based on segment type
            opportunity = self._calculate_segment_opportunity(
                segment_name, customer_count, avg_revenue, avg_frequency
            )
            
            opportunities[segment_name] = opportunity
        
        return opportunities
    
    def _calculate_segment_opportunity(
        self,
        segment_name: str,
        customer_count: int,
        avg_revenue: float,
        avg_frequency: float
    ) -> Dict[str, Any]:
        """Calculate specific opportunity for a segment."""
        
        # Define realistic improvement targets by segment
        improvement_targets = {
            'Champions': {
                'retention_boost': 0.05,  # Keep 5% more
                'frequency_boost': 0.10,  # 10% more orders
                'aov_boost': 0.05,  # 5% higher order value
                'priority': 'HIGH',
                'effort': 'LOW'
            },
            'Loyal Customers': {
                'retention_boost': 0.10,
                'frequency_boost': 0.15,
                'aov_boost': 0.10,
                'priority': 'HIGH',
                'effort': 'MEDIUM'
            },
            'Potential Loyalists': {
                'retention_boost': 0.20,
                'frequency_boost': 0.25,
                'aov_boost': 0.15,
                'priority': 'HIGH',
                'effort': 'MEDIUM'
            },
            'New Customers': {
                'retention_boost': 0.30,  # Get 30% to buy again
                'frequency_boost': 0.50,
                'aov_boost': 0.10,
                'priority': 'CRITICAL',
                'effort': 'HIGH'
            },
            'Promising': {
                'retention_boost': 0.25,
                'frequency_boost': 0.30,
                'aov_boost': 0.15,
                'priority': 'HIGH',
                'effort': 'MEDIUM'
            },
            'Need Attention': {
                'retention_boost': 0.15,
                'frequency_boost': 0.20,
                'aov_boost': 0.10,
                'priority': 'CRITICAL',
                'effort': 'HIGH'
            },
            'About to Sleep': {
                'retention_boost': 0.10,
                'frequency_boost': 0.15,
                'aov_boost': 0.08,
                'priority': 'HIGH',
                'effort': 'HIGH'
            },
            'Hibernating': {
                'retention_boost': 0.05,
                'frequency_boost': 0.10,
                'aov_boost': 0.05,
                'priority': 'MEDIUM',
                'effort': 'HIGH'
            },
            'Lost': {
                'retention_boost': 0.03,
                'frequency_boost': 0.05,
                'aov_boost': 0.05,
                'priority': 'LOW',
                'effort': 'VERY HIGH'
            }
        }
        
        targets = improvement_targets.get(segment_name, {
            'retention_boost': 0.10,
            'frequency_boost': 0.15,
            'aov_boost': 0.10,
            'priority': 'MEDIUM',
            'effort': 'MEDIUM'
        })
        
        # Calculate potential additional revenue
        current_annual_revenue = avg_revenue * customer_count
        
        # Scenario 1: Improve retention
        retained_customers = customer_count * targets['retention_boost']
        retention_revenue_gain = retained_customers * avg_revenue
        
        # Scenario 2: Increase purchase frequency
        frequency_revenue_gain = (avg_revenue / avg_frequency) * targets['frequency_boost'] * customer_count * avg_frequency
        
        # Scenario 3: Increase average order value
        aov_revenue_gain = (avg_revenue / avg_frequency) * targets['aov_boost'] * customer_count * avg_frequency
        
        # Total potential
        total_potential = retention_revenue_gain + frequency_revenue_gain + aov_revenue_gain
        
        # Calculate ROI based on typical marketing costs
        marketing_cost_per_customer = self._estimate_marketing_cost(segment_name)
        total_investment = marketing_cost_per_customer * customer_count
        
        roi = ((total_potential - total_investment) / total_investment * 100) if total_investment > 0 else 0
        
        return {
            'segment': segment_name,
            'customer_count': customer_count,
            'current_annual_revenue': current_annual_revenue,
            'potential_additional_revenue': total_potential,
            'revenue_lift_percentage': (total_potential / current_annual_revenue * 100) if current_annual_revenue > 0 else 0,
            'estimated_investment': total_investment,
            'projected_roi': roi,
            'priority': targets['priority'],
            'effort_level': targets['effort'],
            'scenarios': {
                'retention': {
                    'customers_to_retain': int(retained_customers),
                    'revenue_gain': retention_revenue_gain,
                    'action': 'Implement loyalty program & retention campaigns'
                },
                'frequency': {
                    'additional_orders': int(customer_count * targets['frequency_boost'] * avg_frequency),
                    'revenue_gain': frequency_revenue_gain,
                    'action': 'Cross-sell, email campaigns, exclusive offers'
                },
                'aov': {
                    'aov_increase_target': targets['aov_boost'] * 100,
                    'revenue_gain': aov_revenue_gain,
                    'action': 'Bundles, upsells, free shipping thresholds'
                }
            },
            'quick_wins': self._get_quick_wins(segment_name, customer_count),
            'timeline': self._get_implementation_timeline(segment_name)
        }
    
    def _estimate_marketing_cost(self, segment_name: str) -> float:
        """Estimate marketing cost per customer by segment."""
        # Conservative estimates for Saudi market (in SAR)
        costs = {
            'Champions': 5,  # Low cost - just maintain
            'Loyal Customers': 10,
            'Potential Loyalists': 15,
            'New Customers': 25,  # Higher cost to convert
            'Promising': 20,
            'Need Attention': 30,  # Higher cost to re-engage
            'About to Sleep': 35,
            'Hibernating': 40,
            'Lost': 50  # Highest cost - hardest to win back
        }
        return costs.get(segment_name, 20)
    
    def _get_quick_wins(self, segment_name: str, customer_count: int) -> List[Dict[str, Any]]:
        """Get 3-5 quick win actions for immediate implementation."""
        
        quick_wins = {
            'Champions': [
                {'action': 'Create VIP WhatsApp group', 'timeline': '1 week', 'cost': 'Free', 'impact': 'High'},
                {'action': 'Exclusive early access to new products', 'timeline': '2 weeks', 'cost': 'Low', 'impact': 'High'},
                {'action': 'Birthday/anniversary special offers', 'timeline': '1 week', 'cost': 'Low', 'impact': 'Medium'},
                {'action': 'Request video testimonials', 'timeline': '3 days', 'cost': 'Free', 'impact': 'High'},
                {'action': 'Referral program with rewards', 'timeline': '2 weeks', 'cost': 'Medium', 'impact': 'Very High'}
            ],
            'Loyal Customers': [
                {'action': 'Loyalty points program', 'timeline': '2 weeks', 'cost': 'Medium', 'impact': 'Very High'},
                {'action': 'Thank you note with 10% off next order', 'timeline': '3 days', 'cost': 'Low', 'impact': 'High'},
                {'action': 'Product recommendations based on history', 'timeline': '1 week', 'cost': 'Low', 'impact': 'High'},
                {'action': 'Exclusive member-only sales', 'timeline': '1 week', 'cost': 'Medium', 'impact': 'High'}
            ],
            'Potential Loyalists': [
                {'action': 'Welcome series (3 emails over 2 weeks)', 'timeline': '1 week', 'cost': 'Low', 'impact': 'High'},
                {'action': '15% off second purchase coupon', 'timeline': '3 days', 'cost': 'Medium', 'impact': 'Very High'},
                {'action': 'Product education content via WhatsApp', 'timeline': '1 week', 'cost': 'Low', 'impact': 'Medium'},
                {'action': 'Limited-time bundle offers', 'timeline': '3 days', 'cost': 'Medium', 'impact': 'High'}
            ],
            'New Customers': [
                {'action': 'Welcome discount for 2nd purchase (20%)', 'timeline': '1 day', 'cost': 'High', 'impact': 'Critical'},
                {'action': 'Product care guide & follow-up', 'timeline': '3 days', 'cost': 'Free', 'impact': 'High'},
                {'action': 'Survey with incentive (SAR 10 credit)', 'timeline': '1 week', 'cost': 'Low', 'impact': 'Medium'},
                {'action': 'Complementary product suggestions', 'timeline': '5 days', 'cost': 'Low', 'impact': 'High'}
            ],
            'Promising': [
                {'action': 'Flash sale notification', 'timeline': '2 days', 'cost': 'Low', 'impact': 'High'},
                {'action': 'Free shipping for next order', 'timeline': '1 day', 'cost': 'Medium', 'impact': 'High'},
                {'action': 'Product restock alerts', 'timeline': '1 week', 'cost': 'Free', 'impact': 'Medium'},
                {'action': 'Social proof (bestsellers)', 'timeline': '3 days', 'cost': 'Free', 'impact': 'Medium'}
            ],
            'Need Attention': [
                {'action': 'We miss you - 25% off', 'timeline': '1 day', 'cost': 'High', 'impact': 'Critical'},
                {'action': 'What can we improve? Survey', 'timeline': '3 days', 'cost': 'Low', 'impact': 'High'},
                {'action': 'New arrivals showcase', 'timeline': '5 days', 'cost': 'Low', 'impact': 'Medium'},
                {'action': 'Limited-time exclusive access', 'timeline': '3 days', 'cost': 'Medium', 'impact': 'High'}
            ],
            'About to Sleep': [
                {'action': 'Urgent: Last chance 30% off', 'timeline': '1 day', 'cost': 'Very High', 'impact': 'High'},
                {'action': 'Abandoned cart reminder', 'timeline': '2 days', 'cost': 'Low', 'impact': 'Medium'},
                {'action': 'Personalized win-back email', 'timeline': '3 days', 'cost': 'Low', 'impact': 'High'},
                {'action': 'Free gift with purchase', 'timeline': '5 days', 'cost': 'High', 'impact': 'High'}
            ],
            'Hibernating': [
                {'action': 'Final chance - 40% off', 'timeline': '1 day', 'cost': 'Very High', 'impact': 'Medium'},
                {'action': 'Have you moved on? Survey', 'timeline': '2 days', 'cost': 'Low', 'impact': 'Low'},
                {'action': 'Show major store changes', 'timeline': '1 week', 'cost': 'Low', 'impact': 'Low'}
            ],
            'Lost': [
                {'action': 'Final goodbye - 50% off', 'timeline': '1 day', 'cost': 'Very High', 'impact': 'Low'},
                {'action': 'Exit survey for feedback', 'timeline': '3 days', 'cost': 'Free', 'impact': 'Low'},
                {'action': 'Unsubscribe (stop wasting budget)', 'timeline': '1 day', 'cost': 'Free', 'impact': 'Positive'}
            ]
        }
        
        return quick_wins.get(segment_name, [])
    
    def _get_implementation_timeline(self, segment_name: str) -> Dict[str, str]:
        """Get recommended implementation timeline."""
        
        timelines = {
            'Champions': {
                'immediate': 'Set up VIP communication channel',
                'week_1': 'Launch referral program',
                'week_2': 'Implement exclusive access',
                'month_1': 'Full loyalty tier system',
                'expected_results': 'Within 30 days'
            },
            'New Customers': {
                'immediate': 'Send welcome discount',
                'week_1': 'Follow-up on satisfaction',
                'week_2': 'Send personalized recommendations',
                'month_1': 'Measure repeat purchase rate',
                'expected_results': 'Within 45 days'
            },
            'Need Attention': {
                'immediate': 'Send re-engagement offer',
                'week_1': 'Survey for feedback',
                'week_2': 'Personalized win-back campaign',
                'month_1': 'Evaluate recovered customers',
                'expected_results': 'Within 60 days'
            }
        }
        
        return timelines.get(segment_name, {
            'immediate': 'Implement quick wins',
            'week_1': 'Launch first campaign',
            'week_2': 'Measure initial results',
            'month_1': 'Optimize and scale',
            'expected_results': 'Within 30-60 days'
        })
    
    def calculate_churn_risk(self) -> Dict[str, Any]:
        """Calculate customers at risk of churning."""
        segment_summary = self.rfm_results.get('segment_summary', {})
        
        high_risk = ['About to Sleep', 'Need Attention']
        medium_risk = ['Hibernating', 'Promising']
        
        high_risk_customers = sum(
            segment_summary.get(seg, {}).get('customer_count', 0) 
            for seg in high_risk
        )
        
        high_risk_revenue = sum(
            segment_summary.get(seg, {}).get('total_revenue', 0) 
            for seg in high_risk
        )
        
        medium_risk_customers = sum(
            segment_summary.get(seg, {}).get('customer_count', 0) 
            for seg in medium_risk
        )
        
        medium_risk_revenue = sum(
            segment_summary.get(seg, {}).get('total_revenue', 0) 
            for seg in medium_risk
        )
        
        # Calculate potential loss if not acted upon
        churn_rate = 0.60  # 60% of at-risk customers will churn without action
        potential_loss = (high_risk_revenue + medium_risk_revenue) * churn_rate
        
        return {
            'high_risk_customers': high_risk_customers,
            'high_risk_annual_revenue': high_risk_revenue,
            'medium_risk_customers': medium_risk_customers,
            'medium_risk_annual_revenue': medium_risk_revenue,
            'total_at_risk': high_risk_customers + medium_risk_customers,
            'potential_annual_loss': potential_loss,
            'recovery_cost': (high_risk_customers + medium_risk_customers) * 30,  # SAR 30 per customer
            'net_value_at_risk': potential_loss - ((high_risk_customers + medium_risk_customers) * 30)
        }
    
    def project_revenue_scenarios(self) -> Dict[str, Any]:
        """Project revenue under different scenarios."""
        total_revenue = self.kpis.get('revenue_metrics', {}).get('total_revenue', 0)
        total_customers = self.kpis.get('customer_metrics', {}).get('total_customers', 0)
        
        # Scenario 1: Do nothing (baseline with natural churn)
        baseline_growth = -0.05  # -5% due to churn
        
        # Scenario 2: Basic improvements (implement some actions)
        basic_growth = 0.15  # +15% growth
        
        # Scenario 3: Aggressive improvements (implement all actions)
        aggressive_growth = 0.35  # +35% growth
        
        return {
            'current_annual_revenue': total_revenue,
            'scenarios': {
                'do_nothing': {
                    'growth_rate': baseline_growth,
                    'projected_revenue': total_revenue * (1 + baseline_growth),
                    'change': total_revenue * baseline_growth,
                    'description': 'No action taken - natural churn continues'
                },
                'basic_improvements': {
                    'growth_rate': basic_growth,
                    'projected_revenue': total_revenue * (1 + basic_growth),
                    'change': total_revenue * basic_growth,
                    'description': 'Implement top 3 actions per segment'
                },
                'aggressive_improvements': {
                    'growth_rate': aggressive_growth,
                    'projected_revenue': total_revenue * (1 + aggressive_growth),
                    'change': total_revenue * aggressive_growth,
                    'description': 'Full implementation of all recommendations'
                }
            },
            'recommended_scenario': 'basic_improvements',
            'break_even_improvement': 0.02  # Need just 2% improvement to break even on investments
        }
    
    def get_priority_action_matrix(self) -> List[Dict[str, Any]]:
        """Create priority matrix for actions (Eisenhower Matrix style)."""
        opportunities = self.calculate_segment_opportunities()
        
        matrix = []
        
        for segment_name, opp in opportunities.items():
            impact_score = opp['revenue_lift_percentage']
            effort_score = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'VERY HIGH': 4}.get(opp['effort_level'], 2)
            
            # Categorize into quadrants
            if impact_score > 20 and effort_score <= 2:
                quadrant = 'DO FIRST'
                priority = 1
            elif impact_score > 20 and effort_score > 2:
                quadrant = 'SCHEDULE'
                priority = 2
            elif impact_score <= 20 and effort_score <= 2:
                quadrant = 'DELEGATE'
                priority = 3
            else:
                quadrant = 'ELIMINATE'
                priority = 4
            
            matrix.append({
                'segment': segment_name,
                'quadrant': quadrant,
                'priority': priority,
                'impact_score': impact_score,
                'effort_level': opp['effort_level'],
                'potential_revenue': opp['potential_additional_revenue'],
                'roi': opp['projected_roi'],
                'customer_count': opp['customer_count']
            })
        
        # Sort by priority then by potential revenue
        matrix.sort(key=lambda x: (x['priority'], -x['potential_revenue']))
        
        return matrix
    
    def generate_executive_recommendations(self) -> Dict[str, Any]:
        """Generate CEO-level executive recommendations."""
        
        churn_risk = self.calculate_churn_risk()
        scenarios = self.project_revenue_scenarios()
        priority_matrix = self.get_priority_action_matrix()
        
        # Get top 3 priorities
        top_priorities = priority_matrix[:3]
        
        # Calculate total opportunity from top priorities
        total_opportunity = sum(p['potential_revenue'] for p in top_priorities)
        total_investment = sum(
            self.calculate_segment_opportunities()[p['segment']]['estimated_investment'] 
            for p in top_priorities
        )
        
        return {
            'critical_metrics': {
                'at_risk_customers': churn_risk['total_at_risk'],
                'revenue_at_risk': churn_risk['potential_annual_loss'],
                'recovery_investment': churn_risk['recovery_cost'],
                'net_value_at_risk': churn_risk['net_value_at_risk']
            },
            'top_3_priorities': [
                {
                    'rank': i + 1,
                    'segment': p['segment'],
                    'customer_count': p['customer_count'],
                    'customers': p['customer_count'],  # Alias for UI compatibility
                    'potential_revenue': p['potential_revenue'],
                    'roi_percentage': p['roi'],
                    'quadrant': p['quadrant']
                }
                for i, p in enumerate(top_priorities)
            ],
            'financial_summary': {
                'total_opportunity': total_opportunity,
                'required_investment': total_investment,
                'projected_roi': ((total_opportunity - total_investment) / total_investment * 100) if total_investment > 0 else 0,
                'payback_period_months': (total_investment / (total_opportunity / 12)) if total_opportunity > 0 else 0
            },
            'recommended_action_plan': self._generate_90_day_plan(top_priorities),
            'key_decisions': [
                f"Allocate SAR {total_investment:,.0f} for customer engagement initiatives",
                f"Focus immediately on {top_priorities[0]['segment']} segment ({top_priorities[0]['customer_count']} customers)" if len(top_priorities) > 0 else "No segments available",
                f"Expected ROI: {((total_opportunity - total_investment) / total_investment * 100):.1f}% within 90 days" if total_investment > 0 else "No investment required",
                f"Prevent loss of SAR {churn_risk['potential_annual_loss']:,.0f} from at-risk customers"
            ]
        }
    
    def _generate_90_day_plan(self, top_priorities: List[Dict]) -> Dict[str, List[str]]:
        """Generate a 90-day action plan."""
        
        if len(top_priorities) == 0:
            return {
                'days_1_30': ['Set up data collection', 'Prepare for analysis'],
                'days_31_60': ['Run initial analysis', 'Identify segments'],
                'days_61_90': ['Implement first campaigns', 'Measure results']
            }
        
        return {
            'days_1_30': [
                f"Launch campaigns for {top_priorities[0]['segment']} segment" if len(top_priorities) > 0 else "Identify top segment",
                "Set up tracking for campaign effectiveness",
                "Implement quick wins from top 3 segments" if len(top_priorities) >= 3 else "Implement quick wins",
                "Establish baseline metrics for all segments"
            ],
            'days_31_60': [
                "Analyze first month results",
                f"Expand to {top_priorities[1]['segment']} segment" if len(top_priorities) > 1 else "Expand to additional segments",
                "Optimize campaigns based on data",
                "Scale successful tactics"
            ],
            'days_61_90': [
                "Full rollout across all priority segments",
                "Measure ROI and adjust budget allocation",
                f"Begin work on {top_priorities[2]['segment']} segment" if len(top_priorities) > 2 else "Continue optimization",
                "Prepare report on financial impact"
            ]
        }
