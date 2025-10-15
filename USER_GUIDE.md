# Advanced Analysis for Salla - User Guide

## 🎯 What This App Does

This is a **fully automated analytics platform** for your Salla store exports. Upload your XLSX file and get instant insights about:
- Customer behavior and segmentation (RFM Analysis)
- Revenue trends and patterns
- Product performance
- Customer retention by cohort
- Actionable recommendations for each customer segment

---

## 📊 Understanding Your Analysis Results

### **1. Executive Summary Page**

**What you'll see:**
- **Total Revenue**: Your store's complete revenue during the analyzed period
- **Total Orders**: Number of completed orders
- **Unique Customers**: How many different customers purchased from you
- **Average Order Value (AOV)**: Average amount spent per order
- **Average Customer Lifetime Value (LTV)**: Average total spending per customer
- **New vs Returning Customers**: Split showing customer acquisition vs retention

**Monthly Revenue Trend Chart:**
- Shows how your revenue changed month by month
- Helps identify seasonal patterns and growth trends
- Use this to plan inventory and marketing campaigns

**Customer & Revenue Distribution:**
- Pie charts showing how many customers are new vs returning
- Revenue breakdown to see which group generates more income
- **Key insight**: High returning customer revenue = strong loyalty

**Export Report Button:**
- Download a complete Excel file with all analysis results
- Contains detailed tables for customers, products, segments
- Perfect for sharing with your team or accounting

---

### **2. Customers (RFM) Page**

**What is RFM?**
RFM stands for:
- **R**ecency: How recently did they purchase? (Lower = better)
- **F**requency: How often do they purchase? (Higher = better)
- **M**onetary: How much do they spend? (Higher = better)

**Your 9 Customer Segments:**

1. **Champions** (R:5, F:5, M:5)
   - Your best customers - recent, frequent, big spenders
   - **What to do**: VIP treatment, exclusive offers, loyalty rewards

2. **Loyal Customers** (R:4-5, F:4-5, M:3-5)
   - Regular customers who keep coming back
   - **What to do**: Upsell, cross-sell, referral programs

3. **Potential Loyalists** (R:4-5, F:2-3, M:3-4)
   - Recent customers starting to buy more
   - **What to do**: Nurture with targeted offers, build relationship

4. **New Customers** (R:5, F:1, M:1-3)
   - Just made their first purchase recently
   - **What to do**: Welcome series, encourage second purchase, great service

5. **Promising** (R:3-4, F:1, M:1-2)
   - Recent buyers with potential
   - **What to do**: Engage quickly with personalized recommendations

6. **Need Attention** (R:2-3, F:2-3, M:2-3)
   - Were active but showing signs of slipping away
   - **What to do**: Re-engagement campaigns, special offers, feedback surveys

7. **About to Sleep** (R:2-3, F:1-2, M:1-3)
   - Haven't purchased recently, low engagement
   - **What to do**: Win-back campaigns, reminder of products they viewed

8. **Hibernating** (R:1-2, F:1-2, M:1-2)
   - Inactive for a while but bought before
   - **What to do**: Strong win-back offers, show what's new

9. **Lost** (R:1, F:1-5, M:1-5)
   - Haven't purchased in a very long time
   - **What to do**: Last-chance campaigns, deep discounts, surveys to understand why

**How to Read the Segment Cards:**
- **Total Customers**: Number of customers in this segment
- **Total Revenue**: Combined spending from this segment
- **Avg Revenue/Customer**: Average spending per customer in segment
- **% of Total**: What percentage of your customer base this represents

**The RFM Heatmap:**
- Grid showing customer distribution across R (Recency) and F (Frequency) scores
- Darker colors = more customers in that cell
- Helps visualize where most of your customers fall

---

### **3. Cohorts & Retention Page**

**What is a Cohort?**
A cohort is a group of customers who made their **first purchase in the same month**.

**The Retention Matrix (Heatmap):**
- **Rows (Y-axis)**: Each row is a cohort (first purchase month)
- **Columns (X-axis)**: Months after first purchase (0, 1, 2, 3...)
- **Cell Values**: Percentage of customers who returned to purchase in that month
- **Color**: Darker blue = higher retention percentage

**How to Read It:**
Example: If "2024-01" cohort shows:
- Month 0: 100% (all customers made first purchase)
- Month 1: 25% (25% came back and bought again within 1 month)
- Month 2: 15% (15% were still active in month 2)

**What Good Retention Looks Like:**
- **20%+ retention at Month 1**: Excellent - customers coming back quickly
- **10-15% at Month 3**: Good - you're keeping a solid base
- **<5% at Month 3**: Needs improvement - focus on retention strategies

**What This Tells You:**
- If retention drops sharply: Need better post-purchase experience
- If retention stays flat: Good loyalty, but may need more campaigns
- If certain cohorts perform better: What was different about that time period?

**Empty Matrix?**
If you see "Insufficient data for cohort analysis":
- Most customers are one-time buyers
- Need more time/data to see patterns
- Focus on strategies to encourage repeat purchases

---

### **4. Products Page**

**Top 10 Products by Revenue:**
- Bar chart showing which products generate the most money
- Longer bars = higher revenue products
- **Use this to**:
  - Stock more of your best sellers
  - Feature top products in marketing
  - Identify your "hero" products

**Product Performance Table:**
- **Revenue**: Total sales for each product
- **Units Sold**: How many sold (if available)
- **Unique Customers**: How many different customers bought it
- **AOV**: Average order value when this product is purchased

**Empty Product Page?**
If you see "No product data available":
- Your export file didn't include product names
- Re-export from Salla ensuring product data is included
- Make sure to map the "Product Name" column during upload

---

### **5. Actions & Playbooks Page**

This page gives you **ready-to-implement strategies** for each customer segment.

**For Each Segment:**
- Customer count and revenue contribution
- **Specific action items** you can execute immediately
- Average value per customer in that segment

**Example Actions (Champions segment):**
1. Create VIP exclusive offers
2. Send personalized thank you messages
3. Offer early access to new products
4. Create a loyalty/points program
5. Request testimonials and reviews

**How to Use This Page:**
1. Start with your largest or highest-revenue segments
2. Pick 2-3 actions to implement this week
3. Track results and adjust
4. Move to next segment

**Why This Matters:**
Generic marketing treats all customers the same. Segment-specific actions:
- ✅ Higher engagement rates
- ✅ Better ROI on marketing spend
- ✅ Improved customer satisfaction
- ✅ Increased repeat purchases

---

## 🚀 Quick Start Guide

### Step 1: Upload Your Data
1. Go to "Upload & Map" page (sidebar)
2. Click "Choose XLSX File"
3. Select your Salla export file
4. Wait for automatic column detection (100% confidence on standard exports)

### Step 2: Verify Mappings (if needed)
- App auto-detects all columns for standard Salla exports
- If manual mapping needed, select the correct column for each field
- Required fields: Order ID, Date, Customer ID, Total
- Optional but recommended: Product Name, Quantity, Status

### Step 3: Process & Analyze
1. Click "✓ Process Data"
2. Wait ~25 seconds for analysis to complete
3. Navigation menu will appear automatically

### Step 4: Review Results
Start with this flow:
1. **Executive Summary**: Get overall picture
2. **Customers (RFM)**: Understand your customer base
3. **Actions & Playbooks**: Get specific recommendations
4. **Products**: See what's selling best
5. **Cohorts**: Check retention patterns

### Step 5: Take Action
- Download the Excel report (Summary page bottom)
- Share insights with your team
- Implement recommended actions for top segments
- Re-run analysis monthly to track progress

---

## 💡 Pro Tips

### Understanding Your Numbers

**Good Benchmarks for Saudi E-commerce:**
- **AOV**: SAR 200-500 (varies by industry)
- **Repeat Purchase Rate**: 20-30% is good
- **Month 1 Retention**: 20%+ is excellent
- **Champions + Loyal %**: Should be 15-25% of customer base

**Red Flags:**
- ⚠️ More than 30% Lost + Hibernating segments: Need urgent retention work
- ⚠️ Less than 10% returning customers: Focus on post-purchase experience
- ⚠️ Retention drops to 0% after Month 1: Critical retention issue
- ⚠️ 80%+ revenue from new customers: Unsustainable, need loyalty

### Making the Most of This Tool

1. **Run Monthly**: Track trends and measure improvement
2. **Compare Periods**: Upload different time periods to see changes
3. **Focus on Actions**: Don't just look at numbers - implement the recommendations
4. **Start Small**: Pick 1-2 segments to focus on first
5. **Measure Results**: Re-run analysis after implementing strategies

### Common Questions

**Q: Why is my avg revenue per customer SAR 0.00?**
A: This was a bug - it's now fixed! Refresh the page to see actual values.

**Q: Why are cohorts/products empty?**
A: Either your export doesn't contain that data, or there's insufficient historical data. The app now explains why sections are empty.

**Q: What's the difference between Champions and Loyal Customers?**
A: Champions score 5/5 on all RFM metrics - they're your absolute best. Loyal Customers score 4-5 on most metrics - still excellent but slightly lower.

**Q: Should I worry about Lost customers?**
A: Lost customers (22.4% in your data) are common. Focus on preventing "About to Sleep" and "Need Attention" from becoming Lost through re-engagement.

**Q: How do I improve retention?**
A: 
1. Better post-purchase communication
2. Loyalty/points program  
3. Personalized recommendations
4. Exclusive offers for repeat buyers
5. Follow-up after 30-45 days

---

## 📈 Interpreting Your Specific Data

**Your Current Analysis Shows:**
- **20,901 orders** from **16,023 customers**
- **SAR 14,008,689.27** total revenue
- **Date range**: Nov 2023 - Aug 2025 (22 months)
- **9 customer segments** identified
- **22 cohorts** tracked
- **4,223 products** analyzed

**Your Segment Distribution:**
1. About to Sleep: 24.2% (3,877 customers) - **Priority: Re-engage**
2. Lost: 22.4% (3,596 customers) - **Last-chance campaigns**
3. Champions: 11.5% (1,843 customers) - **VIP treatment**
4. Need Attention: 11.1% (1,781 customers) - **Urgent: Win-back**
5. Loyal: 8.8% (1,414 customers) - **Reward & upsell**
6. New: 8.4% (1,344 customers) - **Nurture for repeat**
7. Hibernating: 6.2% (996 customers) - **Strong offers**
8. Potential Loyalists: 5.7% (916 customers) - **Build relationship**
9. Promising: 1.6% (256 customers) - **Quick engagement**

**Recommended Focus Areas:**
1. **Critical (46.6%)**: About to Sleep + Lost = need immediate attention
2. **High Value (20.3%)**: Champions + Loyal = reward and retain
3. **Growth Opportunity (14.1%)**: New + Potential Loyalists = nurture

---

## 🔄 Regular Usage Workflow

### Weekly:
- Check new customer actions (Actions page)
- Monitor Champions segment for any changes
- Review product performance

### Monthly:
- Upload latest Salla export
- Run full analysis
- Compare to previous month
- Adjust strategies based on segment changes
- Download and archive report

### Quarterly:
- Deep dive into cohort retention trends
- Evaluate which actions worked best
- Set new targets for each segment
- Plan seasonal campaigns

---

## 🆘 Support & Troubleshooting

### Server Issues:
- **Error loading page**: Refresh browser
- **Changes not showing**: Kill and restart Streamlit server
- **Connection refused**: Check if server is running on port 8501

### Data Issues:
- **Only 9 rows loaded**: Check if file corrupted, try re-exporting
- **Columns not detected**: Ensure using standard Salla export format
- **Missing analysis**: Check if required columns (Order ID, Date, Customer ID, Total) are present

### Translation Issues:
- App supports English and Arabic
- Switch language using sidebar dropdown
- All metrics and recommendations translated

---

## 📧 Next Steps

1. **Now**: Refresh your browser and explore the improved UX
2. **Today**: Review Actions page and pick 3 actions to implement
3. **This Week**: Focus on your highest-value segments (Champions, Loyal)
4. **This Month**: Implement re-engagement campaign for "About to Sleep"
5. **Next Month**: Re-run analysis and measure improvement

---

**Remember**: Data without action is just numbers. Use the specific recommendations on the Actions page to drive real business results! 🚀
