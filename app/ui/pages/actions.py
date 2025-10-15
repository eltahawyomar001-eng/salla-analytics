"""Actions and recommendations page."""

import streamlit as st

from app.ui.components import get_translator, format_number, format_currency

def render_actions_page():
    """Render the actions and recommendations page."""
    language = st.session_state.language
    t = get_translator(language)
    
    if not st.session_state.get('data_loaded', False):
        st.warning(t['errors']['no_data'])
        return
    
    st.title(t['actions']['title'])
    st.markdown(t['actions']['description'])
    
    # Add explanation
    st.info("💡 **How to use this page:** Each customer segment has specific recommended actions based on their behavior patterns. Expand each segment to see actionable strategies you can implement immediately to improve customer engagement and revenue.")
    
    rfm_results = st.session_state.analysis_results.get('rfm', {})
    
    if not isinstance(rfm_results, dict) or not rfm_results:
        st.error(t['errors']['no_analysis'])
        return
    
    # Show recommended actions for each segment
    segment_summary = rfm_results.get('segment_summary', {})
    
    st.markdown(f"## {t['actions'].get('segment_actions', 'Segment-Specific Actions')}")
    
    # Define clear actionable strategies for each segment
    segment_actions = {
        'Champions': [
            "🎁 **Create VIP Program**: Set up exclusive WhatsApp group with early access to new products and special discounts",
            "💝 **Birthday Rewards**: Send personalized birthday offers (20% off + free shipping) to strengthen loyalty",
            "🌟 **Request Testimonials**: Ask for video reviews, offer SAR 50 credit for featured testimonials",
            "👥 **Referral Program**: Reward SAR 25 for each successful referral, give referee SAR 25 off first order",
            "📧 **VIP Newsletter**: Monthly exclusive content with tips, behind-the-scenes, and first-look at new products"
        ],
        'Loyal Customers': [
            "🎯 **Loyalty Points**: Earn 1 point per SAR spent, 100 points = SAR 50 discount (launches brand loyalty)",
            "💌 **Thank You Campaign**: Send personalized thank-you note with 10% off next order within 7 days",
            "🛍️ **Smart Recommendations**: Email personalized product suggestions based on purchase history every 2 weeks",
            "🔥 **Member-Only Flash Sales**: 48-hour exclusive sales with 15-25% off selected items",
            "📱 **VIP Support Line**: Dedicated WhatsApp number for priority customer service"
        ],
        'Potential Loyalists': [
            "🎊 **Welcome Series**: 3 automated emails over 2 weeks (day 1: thank you, day 7: tips, day 14: exclusive offer)",
            "💰 **Second Purchase Incentive**: 15% off + free shipping on 2nd order (valid 14 days)",
            "📖 **Product Education**: Send how-to guides, styling tips, or usage tutorials for purchased products",
            "🎁 **Bundle Offers**: Create curated bundles with 20% discount when buying complementary products together",
            "⭐ **Early Access**: Invite to exclusive pre-launch sales 24 hours before public release"
        ],
        'New Customers': [
            "🎉 **Welcome Discount**: IMMEDIATE 20% off coupon for 2nd purchase (expires in 7 days) - CRITICAL for conversion",
            "📦 **Delivery Follow-Up**: WhatsApp message 2 days after delivery asking 'How's your order?' with product care tips",
            "💬 **Quick Survey**: 3-question survey with SAR 10 credit incentive to understand preferences",
            "🔗 **Cross-Sell Email**: Day 5 email suggesting complementary products with 'complete your look' theme",
            "📲 **Add to Social Media**: Invite to follow Instagram/Snapchat with exclusive follower-only discount codes"
        ],
        'Promising': [
            "⚡ **Flash Sale Alert**: SMS/WhatsApp notification for 24-hour flash sales with 25% off",
            "🚚 **Free Shipping Offer**: Next order ships free (no minimum, valid 10 days) to remove purchase barrier",
            "🔔 **Restock Notifications**: Enable 'notify me' for out-of-stock items they viewed",
            "🏆 **Social Proof**: Email showcasing bestsellers and customer photos with 'join 10,000+ happy customers' message",
            "💳 **Payment Options**: Highlight Tamara/Tabby installment options (buy now, pay later)"
        ],
        'Need Attention': [
            "🚨 **URGENT Win-Back**: 'We miss you - 25% OFF' email with personalized product recommendations (send TODAY)",
            "📊 **Feedback Survey**: 'What can we improve?' survey with SAR 15 credit for completion",
            "✨ **New Arrivals Showcase**: Email highlighting new products since their last purchase",
            "🎟️ **Exclusive Access Pass**: Limited-time VIP access to members-only sale (48 hours)",
            "� **Personal Outreach**: For high-value customers, personal WhatsApp message from founder/manager"
        ],
        'About to Sleep': [
            "⏰ **LAST CHANCE**: 'Final chance - 30% OFF everything' with urgency timer (expires in 48 hours)",
            "🛒 **Abandoned Cart**: If they browsed, send abandoned cart email with additional 10% off",
            "💝 **Win-Back Gift**: Free gift with next purchase (e.g., free product sample or branded item)",
            "🔄 **Reactivation Campaign**: 3-email series over 10 days with increasing discounts (15%, 25%, 35%)",
            "📱 **SMS Last Touch**: Final SMS: 'We noticed you haven't been back. Here's 40% off - today only'"
        ],
        'Hibernating': [
            "💔 **Final Offer**: 'Last goodbye offer - 40% OFF' to test if price is the barrier",
            "❓ **Exit Survey**: 'Have you moved on?' survey to understand why they left (offer SAR 20 credit)",
            "🆕 **Show Major Changes**: If you've improved shipping/products/prices, highlight these improvements",
            "🎯 **Retargeting Ads**: Run Facebook/Instagram ads specifically targeting this segment with special offers",
            "✅ **Consider Unsubscribing**: If no response after 3 attempts, remove from email list to save costs"
        ],
        'Lost': [
            "💸 **Final Goodbye**: 'One last chance - 50% OFF' as absolute final attempt (send once only)",
            "📝 **Exit Feedback**: Brief survey asking why they stopped buying (no incentive needed, just closure)",
            "🛑 **STOP MARKETING**: Unsubscribe them from regular emails to avoid spam complaints and save budget",
            "📊 **Analyze Patterns**: Review this segment to understand common issues (shipping? quality? price?)",
            "♻️ **Win-Back Budget**: Reallocate marketing budget from Lost segment to New Customers (better ROI)"
        ]
    }
    
    for segment_name, segment_data in segment_summary.items():
        if segment_data.get('customer_count', 0) == 0:
            continue
        
        actions = segment_actions.get(segment_name, [])
        
        with st.expander(f"📋 {segment_name} ({format_number(segment_data.get('customer_count', 0), language, decimals=0)} customers)", expanded=False):
            
            # Show clear actionable strategies first
            if actions:
                st.markdown("### 🎯 Immediate Action Plan")
                st.markdown("**Implement these strategies THIS WEEK:**\n")
                for action in actions:
                    st.markdown(action)
                st.markdown("")
                st.markdown("---")
            else:
                st.warning("No specific actions defined for this segment yet.")
            
            # Show segment metrics
            st.markdown("### 📊 Segment Metrics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    t['customers']['total_customers'],
                    format_number(segment_data.get('customer_count', 0), language, decimals=0)
                )
            
            with col2:
                st.metric(
                    t['summary']['total_revenue'],
                    format_currency(segment_data.get('total_revenue', 0), language=language)
                )
            
            with col3:
                st.metric(
                    t['customers'].get('avg_revenue_per_customer', 'Avg Revenue/Customer'),
                    format_currency(segment_data.get('avg_revenue_per_customer', 0), language=language)
                )