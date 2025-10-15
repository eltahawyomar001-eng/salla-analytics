"""Business metrics explanations and insights for Salla analytics."""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class BusinessExplainer:
    """Provides business explanations and insights for analytics metrics."""
    
    def __init__(self, language: str = 'en'):
        self.language = language
        self.explanations = self._load_explanations()
        
    def _load_explanations(self) -> Dict[str, Any]:
        """Load business explanations from configuration."""
        # For now, return built-in explanations
        # In production, this could load from external files
        return {
            'kpis': {
                'total_revenue': {
                    'en': {
                        'definition': "Total revenue is the sum of all order values before any deductions.",
                        'importance': "This is your top-line metric indicating overall business size and growth.",
                        'interpretation': "Higher values indicate stronger business performance, but consider trends over time.",
                        'actions': [
                            "Track monthly trends to identify growth patterns",
                            "Compare against industry benchmarks",
                            "Analyze revenue sources and channels"
                        ]
                    },
                    'ar': {
                        'definition': "إجمالي الإيرادات هو مجموع جميع قيم الطلبات قبل أي خصومات.",
                        'importance': "هذا هو المقياس الأساسي الذي يشير إلى حجم الأعمال ونموها الإجمالي.",
                        'interpretation': "القيم الأعلى تشير إلى أداء أعمال أقوى، لكن انظر إلى الاتجاهات عبر الوقت.",
                        'actions': [
                            "تتبع الاتجاهات الشهرية لتحديد أنماط النمو",
                            "قارن مع معايير الصناعة",
                            "حلل مصادر الإيرادات والقنوات"
                        ]
                    }
                },
                'average_order_value': {
                    'en': {
                        'definition': "Average Order Value (AOV) is the average amount spent per order.",
                        'importance': "AOV indicates customer spending behavior and pricing effectiveness.",
                        'interpretation': "Higher AOV suggests customers find value in your products or successful upselling.",
                        'actions': [
                            "Implement product bundling strategies",
                            "Create minimum order incentives",
                            "Focus on upselling and cross-selling"
                        ]
                    },
                    'ar': {
                        'definition': "متوسط قيمة الطلب هو المتوسط المنفق لكل طلب.",
                        'importance': "يشير إلى سلوك إنفاق العملاء وفعالية التسعير.",
                        'interpretation': "القيمة الأعلى تشير إلى أن العملاء يجدون قيمة في منتجاتك أو نجاح البيع الإضافي.",
                        'actions': [
                            "تطبيق استراتيجيات حزم المنتجات",
                            "إنشاء حوافز الحد الأدنى للطلب",
                            "التركيز على البيع الإضافي والمتقاطع"
                        ]
                    }
                },
                'repeat_rate': {
                    'en': {
                        'definition': "Repeat rate is the percentage of customers who made more than one purchase.",
                        'importance': "Indicates customer loyalty and satisfaction with your products/service.",
                        'interpretation': "Higher repeat rates suggest strong customer retention and business sustainability.",
                        'actions': [
                            "Implement loyalty programs",
                            "Improve customer service experience",
                            "Send follow-up communications",
                            "Gather and act on customer feedback"
                        ]
                    },
                    'ar': {
                        'definition': "معدل التكرار هو نسبة العملاء الذين قاموا بأكثر من عملية شراء واحدة.",
                        'importance': "يشير إلى ولاء العملاء ورضاهم عن منتجاتك/خدمتك.",
                        'interpretation': "معدلات التكرار الأعلى تشير إلى احتفاظ قوي بالعملاء واستدامة الأعمال.",
                        'actions': [
                            "تطبيق برامج الولاء",
                            "تحسين تجربة خدمة العملاء",
                            "إرسال تواصل متابعة",
                            "جمع ملاحظات العملاء والعمل عليها"
                        ]
                    }
                }
            },
            'rfm_segments': {
                'Champions': {
                    'en': {
                        'definition': "Your best customers who bought recently, frequently, and spend the most.",
                        'characteristics': "High recency, frequency, and monetary scores (4-5 across all dimensions).",
                        'business_value': "These customers drive significant revenue and are likely to continue doing so.",
                        'actions': [
                            "Reward them with exclusive offers and early access",
                            "Make them brand ambassadors through referral programs",
                            "Ask for reviews and testimonials",
                            "Provide premium customer service",
                            "Offer loyalty program benefits"
                        ],
                        'warning': "Don't take these customers for granted - competitors may target them."
                    },
                    'ar': {
                        'definition': "أفضل عملائك الذين اشتروا مؤخراً وبكثرة وينفقون أكثر.",
                        'characteristics': "درجات عالية في الحداثة والتكرار والقيمة النقدية (4-5 في جميع الأبعاد).",
                        'business_value': "هؤلاء العملاء يحققون إيرادات كبيرة ومن المرجح أن يستمروا في ذلك.",
                        'actions': [
                            "كافئهم بعروض حصرية ووصول مبكر",
                            "اجعلهم سفراء للعلامة التجارية من خلال برامج الإحالة",
                            "اطلب منهم المراجعات والشهادات",
                            "قدم خدمة عملاء متميزة",
                            "اعرض مزايا برنامج الولاء"
                        ],
                        'warning': "لا تأخذ هؤلاء العملاء كأمر مسلم به - قد يستهدفهم المنافسون."
                    }
                },
                'At Risk': {
                    'en': {
                        'definition': "High-value customers who haven't purchased recently and may be churning.",
                        'characteristics': "Low recency but high frequency and monetary scores.",
                        'business_value': "These customers represent significant lost revenue if they churn completely.",
                        'actions': [
                            "Create urgent win-back campaigns",
                            "Offer significant discounts or free shipping",
                            "Reach out personally via phone or email",
                            "Survey them about their experience",
                            "Provide exclusive offers to return"
                        ],
                        'urgency': "High - immediate action required to prevent churn."
                    },
                    'ar': {
                        'definition': "عملاء عاليو القيمة لم يشتروا مؤخراً وقد يكونون في طريقهم للفقدان.",
                        'characteristics': "حداثة منخفضة لكن درجات عالية في التكرار والقيمة النقدية.",
                        'business_value': "هؤلاء العملاء يمثلون إيرادات مفقودة كبيرة إذا فُقدوا تماماً.",
                        'actions': [
                            "إنشاء حملات استرداد عاجلة",
                            "عرض خصومات كبيرة أو شحن مجاني",
                            "التواصل شخصياً عبر الهاتف أو الإيميل",
                            "استطلاع رأيهم حول تجربتهم",
                            "تقديم عروض حصرية للعودة"
                        ],
                        'urgency': "عالية - مطلوب إجراء فوري لمنع الفقدان."
                    }
                }
            },
            'cohort_analysis': {
                'retention_rate': {
                    'en': {
                        'definition': "Percentage of customers from a cohort who return to make another purchase in subsequent periods.",
                        'importance': "Measures how well you retain customers over time.",
                        'benchmark': "Good retention rates vary by industry, but 20-30% after 3 months is often considered healthy for e-commerce.",
                        'interpretation': [
                            "Higher retention = stronger customer relationships",
                            "Declining retention may indicate service issues",
                            "Seasonal patterns are normal in many businesses"
                        ]
                    },
                    'ar': {
                        'definition': "نسبة العملاء من مجموعة معينة الذين يعودون لإجراء شراء آخر في الفترات اللاحقة.",
                        'importance': "يقيس مدى جودة احتفاظك بالعملاء عبر الوقت.",
                        'benchmark': "معدلات الاحتفاظ الجيدة تختلف حسب الصناعة، لكن 20-30% بعد 3 أشهر غالباً ما تُعتبر صحية للتجارة الإلكترونية.",
                        'interpretation': [
                            "احتفاظ أعلى = علاقات عملاء أقوى",
                            "تراجع الاحتفاظ قد يشير إلى مشاكل في الخدمة",
                            "الأنماط الموسمية طبيعية في العديد من الأعمال"
                        ]
                    }
                }
            },
            'anomalies': {
                'high_revenue_day': {
                    'en': {
                        'explanation': "This day showed unusually high revenue compared to typical patterns.",
                        'possible_causes': [
                            "Successful marketing campaign",
                            "Seasonal demand spike",
                            "Product launch or promotion",
                            "External events driving traffic"
                        ],
                        'actions': [
                            "Analyze what drove the spike",
                            "Try to replicate successful strategies",
                            "Ensure inventory can handle similar spikes"
                        ]
                    },
                    'ar': {
                        'explanation': "هذا اليوم أظهر إيرادات عالية بشكل غير عادي مقارنة بالأنماط النموذجية.",
                        'possible_causes': [
                            "حملة تسويقية ناجحة",
                            "ارتفاع طلب موسمي",
                            "إطلاق منتج أو ترويج",
                            "أحداث خارجية تؤدي إلى زيادة الزيارات"
                        ],
                        'actions': [
                            "حلل ما الذي أدى إلى الارتفاع",
                            "حاول تكرار الاستراتيجيات الناجحة",
                            "تأكد من أن المخزون يمكنه التعامل مع ارتفاعات مماثلة"
                        ]
                    }
                }
            }
        }
    
    def explain_metric(self, metric_type: str, metric_name: str) -> Dict[str, Any]:
        """Get explanation for a specific metric."""
        explanations = self.explanations.get(metric_type, {})
        metric_explanation = explanations.get(metric_name, {})
        
        if self.language in metric_explanation:
            return metric_explanation[self.language]
        elif 'en' in metric_explanation:
            return metric_explanation['en']
        else:
            return {
                'definition': f"No explanation available for {metric_name}",
                'importance': "Metric explanation not found",
                'actions': []
            }
    
    def explain_kpi(self, kpi_name: str) -> Dict[str, Any]:
        """Get explanation for a KPI."""
        return self.explain_metric('kpis', kpi_name)
    
    def explain_rfm_segment(self, segment_name: str) -> Dict[str, Any]:
        """Get explanation for an RFM segment."""
        return self.explain_metric('rfm_segments', segment_name)
    
    def explain_cohort_metric(self, metric_name: str) -> Dict[str, Any]:
        """Get explanation for a cohort analysis metric."""
        return self.explain_metric('cohort_analysis', metric_name)
    
    def explain_anomaly(self, anomaly_type: str) -> Dict[str, Any]:
        """Get explanation for an anomaly type."""
        return self.explain_metric('anomalies', anomaly_type)
    
    def get_insights_for_kpis(self, kpis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate business insights based on KPI values."""
        insights = []
        
        # Revenue insights
        revenue_metrics = kpis.get('revenue_metrics', {})
        if revenue_metrics:
            total_revenue = revenue_metrics.get('total_revenue', 0)
            if total_revenue > 0:
                insights.append({
                    'type': 'revenue',
                    'title': 'Revenue Performance' if self.language == 'en' else 'أداء الإيرادات',
                    'message': f"Total revenue of {total_revenue:,.2f} indicates business activity" if self.language == 'en' 
                              else f"إجمالي الإيرادات {total_revenue:,.2f} يشير إلى نشاط تجاري",
                    'metric_value': total_revenue,
                    'explanation': self.explain_kpi('total_revenue')
                })
        
        # Customer insights
        customer_metrics = kpis.get('customer_metrics', {})
        if customer_metrics:
            repeat_rate = customer_metrics.get('repeat_rate', 0)
            if repeat_rate > 0:
                if repeat_rate < 20:
                    level = 'low'
                    message = "Low repeat rate suggests opportunity to improve customer retention" if self.language == 'en' else "معدل التكرار المنخفض يشير إلى فرصة لتحسين احتفاظ العملاء"
                elif repeat_rate < 40:
                    level = 'moderate'
                    message = "Moderate repeat rate shows some customer loyalty" if self.language == 'en' else "معدل التكرار المتوسط يظهر بعض ولاء العملاء"
                else:
                    level = 'good'
                    message = "Good repeat rate indicates strong customer loyalty" if self.language == 'en' else "معدل التكرار الجيد يشير إلى ولاء قوي للعملاء"
                
                insights.append({
                    'type': 'customer_loyalty',
                    'level': level,
                    'title': 'Customer Retention' if self.language == 'en' else 'احتفاظ العملاء',
                    'message': message,
                    'metric_value': repeat_rate,
                    'explanation': self.explain_kpi('repeat_rate')
                })
        
        # Order insights
        order_metrics = kpis.get('order_metrics', {})
        if order_metrics:
            aov = order_metrics.get('average_order_value', 0)
            if aov > 0:
                insights.append({
                    'type': 'order_value',
                    'title': 'Average Order Value' if self.language == 'en' else 'متوسط قيمة الطلب',
                    'message': f"Average order value of {aov:,.2f} per order" if self.language == 'en' 
                              else f"متوسط قيمة الطلب {aov:,.2f} لكل طلب",
                    'metric_value': aov,
                    'explanation': self.explain_kpi('average_order_value')
                })
        
        return insights
    
    def get_segment_recommendations(self, segment_summary: Dict[str, Any]) -> Dict[str, List[str]]:
        """Get recommendations for each customer segment."""
        recommendations = {}
        
        for segment, stats in segment_summary.items():
            customer_count = stats.get('customer_count', 0)
            revenue_percentage = stats.get('percentage_of_revenue', 0)
            
            if customer_count > 0:
                segment_explanation = self.explain_rfm_segment(segment)
                actions = segment_explanation.get('actions', [])
                
                # Add context-specific recommendations
                if revenue_percentage > 30:
                    priority_note = "High Priority - Major revenue contributor" if self.language == 'en' else "أولوية عالية - مساهم رئيسي في الإيرادات"
                elif revenue_percentage > 10:
                    priority_note = "Medium Priority - Significant segment" if self.language == 'en' else "أولوية متوسطة - شريحة مهمة"
                else:
                    priority_note = "Lower Priority - Small segment" if self.language == 'en' else "أولوية أقل - شريحة صغيرة"
                
                recommendations[segment] = [priority_note] + actions
        
        return recommendations
    
    def get_data_quality_insights(self, validation_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get insights about data quality issues."""
        insights = []
        
        if not validation_results.get('is_valid', True):
            errors = validation_results.get('errors', [])
            warnings = validation_results.get('warnings', [])
            
            if errors:
                insights.append({
                    'type': 'data_error',
                    'severity': 'high',
                    'title': 'Data Quality Issues' if self.language == 'en' else 'مشاكل جودة البيانات',
                    'message': 'Critical data issues found that may affect analysis accuracy' if self.language == 'en' 
                              else 'وُجدت مشاكل بيانات حرجة قد تؤثر على دقة التحليل',
                    'details': errors[:3]  # Show top 3 errors
                })
            
            if warnings:
                insights.append({
                    'type': 'data_warning',
                    'severity': 'medium',
                    'title': 'Data Quality Warnings' if self.language == 'en' else 'تحذيرات جودة البيانات',
                    'message': 'Some data quality issues detected' if self.language == 'en' 
                              else 'تم اكتشاف بعض مشاكل جودة البيانات',
                    'details': warnings[:3]  # Show top 3 warnings
                })
        
        return insights
    
    def get_business_recommendations(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get high-level business recommendations based on complete analysis."""
        recommendations = []
        
        # Extract key metrics
        kpis = analysis_results.get('kpis', {})
        rfm_summary = analysis_results.get('rfm_summary', {})
        
        # Revenue growth opportunities
        revenue_metrics = kpis.get('revenue_metrics', {})
        if revenue_metrics:
            recommendations.append({
                'category': 'revenue_growth',
                'priority': 'high',
                'title': 'Revenue Growth Opportunities' if self.language == 'en' else 'فرص نمو الإيرادات',
                'recommendations': [
                    'Focus on increasing average order value through bundling',
                    'Implement targeted marketing for high-value segments',
                    'Develop retention strategies for at-risk customers'
                ] if self.language == 'en' else [
                    'التركيز على زيادة متوسط قيمة الطلب من خلال التجميع',
                    'تطبيق تسويق مستهدف للشرائح عالية القيمة',
                    'تطوير استراتيجيات احتفاظ للعملاء المعرضين للخطر'
                ]
            })
        
        # Customer retention
        customer_metrics = kpis.get('customer_metrics', {})
        if customer_metrics:
            repeat_rate = customer_metrics.get('repeat_rate', 0)
            if repeat_rate < 30:
                recommendations.append({
                    'category': 'customer_retention',
                    'priority': 'high',
                    'title': 'Customer Retention Focus' if self.language == 'en' else 'التركيز على احتفاظ العملاء',
                    'recommendations': [
                        'Implement loyalty programs to encourage repeat purchases',
                        'Improve post-purchase follow-up communications',
                        'Analyze customer feedback for service improvements'
                    ] if self.language == 'en' else [
                        'تطبيق برامج ولاء لتشجيع المشتريات المتكررة',
                        'تحسين تواصل المتابعة بعد الشراء',
                        'تحليل ملاحظات العملاء لتحسين الخدمة'
                    ]
                })
        
        return recommendations

def get_business_explanation(metric_type: str, metric_name: str, language: str = 'en') -> Dict[str, Any]:
    """
    Convenience function to get business explanation for a metric.
    
    Args:
        metric_type: Type of metric (kpis, rfm_segments, etc.)
        metric_name: Name of the specific metric
        language: Language for explanation (en/ar)
        
    Returns:
        Explanation dictionary
    """
    explainer = BusinessExplainer(language)
    return explainer.explain_metric(metric_type, metric_name)