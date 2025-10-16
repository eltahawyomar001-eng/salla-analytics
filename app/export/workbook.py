"""Excel export module for generating comprehensive business reports."""

import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
import logging
from io import BytesIO

try:
    import xlsxwriter
    XLSXWRITER_AVAILABLE = True
except ImportError:
    XLSXWRITER_AVAILABLE = False

from app.config import APP_NAME, APP_VERSION, DEFAULT_CURRENCY

logger = logging.getLogger(__name__)


class ExcelReportGenerator:
    """Generate comprehensive Excel reports with formatting."""
    
    def __init__(self, language: str = 'en'):
        """Initialize the report generator.
        
        Args:
            language: Language code for translations
        """
        self.language = language
        
    def generate_report(
        self,
        df_clean: pd.DataFrame,
        analysis_results: Dict[str, Any],
        validation_report: Dict[str, Any],
        translations: Dict[str, Any]
    ) -> BytesIO:
        """Generate comprehensive Excel report.
        
        Args:
            df_clean: Cleaned dataframe
            analysis_results: All analysis results
            validation_report: Data validation results
            translations: Translation dictionary
            
        Returns:
            BytesIO object containing the Excel file
        """
        if not XLSXWRITER_AVAILABLE:
            raise ImportError("xlsxwriter is required for Excel export")
        
        output = BytesIO()
        
        # Create workbook
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            # Define formats
            formats = self._create_formats(workbook)
            
            # 1. Executive Summary
            self._create_executive_summary(
                writer, workbook, formats, analysis_results, translations
            )
            
            # 2. KPIs Sheet
            self._create_kpis_sheet(
                writer, workbook, formats, analysis_results.get('kpis', {}), translations
            )
            
            # 3. RFM Customers with Business Explanations
            self._create_rfm_detailed_sheet(
                writer, workbook, formats, df_clean, analysis_results.get('rfm', {}), translations
            )
            
            # 4. Segments Summary
            self._create_segments_sheet(
                writer, workbook, formats, analysis_results.get('rfm', {}), translations
            )
            
            # 5. Financial Analysis per Segment
            self._create_financial_analysis_sheet(
                writer, workbook, formats, analysis_results, translations
            )
            
            # 6. Cohorts
            self._create_cohorts_sheet(
                writer, workbook, formats, analysis_results.get('cohorts', {}), translations
            )
            
            # 7. Products
            self._create_products_sheet(
                writer, workbook, formats, analysis_results.get('products', {}), translations
            )
            
            # 8. Anomalies
            self._create_anomalies_sheet(
                writer, workbook, formats, analysis_results.get('anomalies', {}), translations
            )
            
            # 9. Financial Assumptions
            self._create_financial_assumptions_sheet(
                writer, workbook, formats, analysis_results, translations
            )
            
            # 10. Data Dictionary
            self._create_data_dictionary(
                writer, workbook, formats, translations
            )
            
            # 11. Run Log
            self._create_run_log(
                writer, workbook, formats, df_clean, validation_report, translations
            )
        
        output.seek(0)
        return output
    
    def _create_formats(self, workbook: Any) -> Dict[str, Any]:
        """Create Excel formats for styling.
        
        Args:
            workbook: XlsxWriter workbook object
            
        Returns:
            Dictionary of format objects
        """
        return {
            'title': workbook.add_format({
                'bold': True,
                'font_size': 16,
                'align': 'center',
                'valign': 'vcenter',
                'bg_color': '#2E8B57',
                'font_color': 'white'
            }),
            'header': workbook.add_format({
                'bold': True,
                'font_size': 12,
                'bg_color': '#4CAF50',
                'font_color': 'white',
                'border': 1
            }),
            'subheader': workbook.add_format({
                'bold': True,
                'font_size': 11,
                'bg_color': '#E8F5E9',
                'border': 1
            }),
            'number': workbook.add_format({
                'num_format': '#,##0',
                'border': 1
            }),
            'currency': workbook.add_format({
                'num_format': '#,##0.00',  # Generic number format without currency symbol
                'border': 1
            }),
            'percent': workbook.add_format({
                'num_format': '0.0%',
                'border': 1
            }),
            'date': workbook.add_format({
                'num_format': 'yyyy-mm-dd',
                'border': 1
            }),
            'text': workbook.add_format({
                'border': 1
            }),
            'wrap': workbook.add_format({
                'text_wrap': True,
                'border': 1,
                'valign': 'top'
            })
        }
    
    def _create_executive_summary(
        self,
        writer: pd.ExcelWriter,
        workbook: Any,
        formats: Dict[str, Any],
        analysis_results: Dict[str, Any],
        translations: Dict[str, Any]
    ):
        """Create executive summary sheet."""
        worksheet = workbook.add_worksheet('1_Executive_Summary')
        
        # Title
        worksheet.merge_range('A1:D1', f'{APP_NAME} - Executive Summary', formats['title'])
        worksheet.set_row(0, 25)
        
        # Key metrics
        kpis = analysis_results.get('kpis', {})
        revenue_metrics = kpis.get('revenue_metrics', {})
        customer_metrics = kpis.get('customer_metrics', {})
        order_metrics = kpis.get('order_metrics', {})
        
        row = 2
        
        # Revenue section
        worksheet.write(row, 0, 'REVENUE METRICS', formats['subheader'])
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:B', 20)
        row += 1
        
        metrics = [
            ('Total Revenue', revenue_metrics.get('total_revenue', 0), 'currency'),
            ('Average Revenue', revenue_metrics.get('mean_revenue', 0), 'currency'),
            ('Median Revenue', revenue_metrics.get('median_revenue', 0), 'currency'),
        ]
        
        for label, value, fmt in metrics:
            worksheet.write(row, 0, label, formats['text'])
            worksheet.write(row, 1, value, formats[fmt])
            row += 1
        
        row += 1
        
        # Customer section
        worksheet.write(row, 0, 'CUSTOMER METRICS', formats['subheader'])
        row += 1
        
        metrics = [
            ('Total Customers', customer_metrics.get('total_customers', 0), 'number'),
            ('New Customers', customer_metrics.get('new_customers', 0), 'number'),
            ('Returning Customers', customer_metrics.get('returning_customers', 0), 'number'),
            ('Repeat Purchase Rate', customer_metrics.get('repeat_purchase_rate', 0), 'percent'),
            ('Average Customer LTV', customer_metrics.get('avg_customer_ltv', 0), 'currency'),
        ]
        
        for label, value, fmt in metrics:
            worksheet.write(row, 0, label, formats['text'])
            worksheet.write(row, 1, value, formats[fmt])
            row += 1
        
        row += 1
        
        # Order section
        worksheet.write(row, 0, 'ORDER METRICS', formats['subheader'])
        row += 1
        
        metrics = [
            ('Total Orders', order_metrics.get('total_orders', 0), 'number'),
            ('Average Order Value', order_metrics.get('average_order_value', 0), 'currency'),
            ('Orders Per Day', order_metrics.get('orders_per_day', 0), 'number'),
        ]
        
        for label, value, fmt in metrics:
            worksheet.write(row, 0, label, formats['text'])
            worksheet.write(row, 1, value, formats[fmt])
            row += 1
    
    def _create_kpis_sheet(
        self,
        writer: pd.ExcelWriter,
        workbook: Any,
        formats: Dict[str, Any],
        kpis: Dict[str, Any],
        translations: Dict[str, Any]
    ):
        """Create detailed KPIs sheet."""
        worksheet = workbook.add_worksheet('2_KPIs')
        
        # Title
        worksheet.merge_range('A1:C1', 'Key Performance Indicators', formats['title'])
        worksheet.set_row(0, 25)
        
        # Write all KPIs in structured format
        row = 2
        worksheet.write(row, 0, 'Category', formats['header'])
        worksheet.write(row, 1, 'Metric', formats['header'])
        worksheet.write(row, 2, 'Value', formats['header'])
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 35)
        worksheet.set_column('C:C', 20)
        
        row += 1
        
        # Flatten KPIs for display
        for category, metrics in kpis.items():
            if isinstance(metrics, dict):
                for metric, value in metrics.items():
                    if isinstance(value, (int, float)):
                        worksheet.write(row, 0, category.replace('_', ' ').title(), formats['text'])
                        worksheet.write(row, 1, metric.replace('_', ' ').title(), formats['text'])
                        
                        if 'revenue' in metric or 'value' in metric or 'ltv' in metric:
                            worksheet.write(row, 2, value, formats['currency'])
                        elif 'rate' in metric or 'percentage' in metric:
                            worksheet.write(row, 2, value, formats['percent'])
                        else:
                            worksheet.write(row, 2, value, formats['number'])
                        
                        row += 1
    
    def _create_rfm_sheet(
        self,
        writer: pd.ExcelWriter,
        workbook: Any,
        formats: Dict[str, Any],
        rfm_results: Dict[str, Any],
        translations: Dict[str, Any]
    ):
        """Create RFM customers sheet."""
        try:
            # Try both 'rfm_data' (new) and 'rfm_dataframe' (old) keys
            rfm_df = rfm_results.get('rfm_data')
            if rfm_df is None:
                rfm_df = rfm_results.get('rfm_dataframe')
            
            if rfm_df is None:
                return
            
            if not isinstance(rfm_df, pd.DataFrame):
                return
            
            if len(rfm_df) == 0:
                return
            
            # Write to sheet
            rfm_df.to_excel(writer, sheet_name='3_RFM_Customers', index=False)
            
            worksheet = writer.sheets['3_RFM_Customers']
            
            # Format headers
            for col_num, value in enumerate(rfm_df.columns.values):
                worksheet.write(0, col_num, value, formats['header'])
            
            # Set column widths
            worksheet.set_column('A:A', 15)  # customer_id
            worksheet.set_column('B:D', 12)  # R, F, M scores
            worksheet.set_column('E:E', 20)  # segment
            worksheet.set_column('F:G', 15)  # metrics
        except Exception as e:
            logger.warning(f"Failed to create RFM sheet: {e}")
            return
    
    def _create_rfm_detailed_sheet(
        self,
        writer: pd.ExcelWriter,
        workbook: Any,
        formats: Dict[str, Any],
        df_clean: pd.DataFrame,
        rfm_results: Dict[str, Any],
        translations: Dict[str, Any]
    ):
        """Create detailed RFM sheet with business explanations."""
        try:
            logger.info("Starting detailed RFM sheet creation...")
            
            # Get RFM data - check both possible keys
            rfm_df = rfm_results.get('rfm_data')
            if rfm_df is None:
                rfm_df = rfm_results.get('rfm_dataframe')
            
            if rfm_df is None or not isinstance(rfm_df, pd.DataFrame) or len(rfm_df) == 0:
                logger.warning("RFM data not available or empty")
                return
            
            logger.info(f"RFM data has {len(rfm_df)} rows and {len(rfm_df.columns)} columns")
            
            # Merge with original data to get customer details
            logger.info("Grouping customer summary data...")
            customer_summary = df_clean.groupby('customer_id').agg({
                'order_total': ['sum', 'mean', 'count'],
                'order_date': ['min', 'max']
            }).reset_index()
            
            customer_summary.columns = ['customer_id', 'total_spent', 'avg_order', 'num_orders', 'first_order', 'last_order']
            logger.info(f"Customer summary created with {len(customer_summary)} rows")
            
            # Merge with RFM data
            logger.info("Merging RFM data with customer summary...")
            detailed_df = rfm_df.merge(customer_summary, on='customer_id', how='left')
            logger.info(f"Merged data has {len(detailed_df)} rows and {len(detailed_df.columns)} columns")
            
            # Determine column names to use
            logger.info("Determining column names...")
            recency_col = 'recency' if 'recency' in list(detailed_df.columns) else 'R'
            frequency_col = 'frequency' if 'frequency' in list(detailed_df.columns) else 'F'
            monetary_col = 'monetary' if 'monetary' in list(detailed_df.columns) else 'M'
            logger.info(f"Using columns: {recency_col}, {frequency_col}, {monetary_col}")
            
            # Add business explanations using vectorized operations where possible
            logger.info("Adding business explanations...")
            detailed_df['Recency_Explanation'] = detailed_df[recency_col].apply(self._explain_recency)
            logger.info("Added Recency_Explanation")
            detailed_df['Frequency_Explanation'] = detailed_df[frequency_col].apply(self._explain_frequency)
            logger.info("Added Frequency_Explanation")
            detailed_df['Monetary_Explanation'] = detailed_df[monetary_col].apply(self._explain_monetary)
            logger.info("Added Monetary_Explanation")
            detailed_df['Segment_Explanation'] = detailed_df['segment'].apply(self._explain_segment)
            logger.info("Added Segment_Explanation")
            detailed_df['Business_Recommendation'] = detailed_df['segment'].apply(self._get_recommendation)
            logger.info("Added Business_Recommendation")
            detailed_df['Priority_Level'] = detailed_df['segment'].apply(self._get_priority)
            logger.info("Added Priority_Level")
            detailed_df['Expected_Action'] = detailed_df['segment'].apply(self._get_expected_action)
            logger.info("Added Expected_Action")
            
            # Reorder columns for clarity
            column_order = [
                'customer_id', 'segment', 'Priority_Level',
                recency_col,
                frequency_col,
                monetary_col,
                'total_spent', 'avg_order', 'num_orders',
                'first_order', 'last_order',
                'Segment_Explanation', 'Recency_Explanation',
                'Frequency_Explanation', 'Monetary_Explanation',
                'Business_Recommendation', 'Expected_Action'
            ]
            
            # Filter to only existing columns
            available_cols = list(detailed_df.columns)
            column_order = [col for col in column_order if col in available_cols]
            detailed_df = detailed_df[column_order]
            
            # Write to Excel
            detailed_df.to_excel(writer, sheet_name='Customer_Analysis_RFM', index=False, startrow=1)
            
            worksheet = writer.sheets['Customer_Analysis_RFM']
            
            # Add title
            worksheet.merge_range(0, 0, 0, len(column_order)-1, '🎯 Customer Analysis (RFM) - Business Intelligence Report', formats['title'])
            
            # Format headers with explanations
            header_explanations = {
                'customer_id': 'Unique customer identifier',
                'segment': 'Customer classification based on RFM analysis',
                'Priority_Level': 'Business priority (High/Medium/Low)',
                'recency': 'Days since last purchase (Lower = better)',
                'R': 'Days since last purchase (Lower = better)',
                'frequency': 'Total number of orders (Higher = better)',
                'F': 'Total number of orders (Higher = better)',
                'monetary': 'Total revenue from customer (Higher = better)',
                'M': 'Total revenue from customer (Higher = better)',
                'total_spent': 'Lifetime value - all revenue',
                'avg_order': 'SAR per order on average (Good order value)',
                'num_orders': 'Count of all orders',
                'first_order': 'Date of first purchase',
                'last_order': 'Date of most recent purchase',
                'Segment_Explanation': 'What this customer segment means',
                'Recency_Explanation': 'How recent their purchases are',
                'Frequency_Explanation': 'How often they buy',
                'Monetary_Explanation': 'How much they spend',
                'Business_Recommendation': 'Specific action to take',
                'Expected_Action': 'Immediate next step'
            }
            
            for col_num, col_name in enumerate(column_order):
                explanation = header_explanations.get(col_name, '')
                if explanation:
                    worksheet.write_comment(1, col_num, explanation)
                worksheet.write(1, col_num, col_name, formats['header'])
            
            # Set column widths
            widths = [15, 20, 12, 12, 12, 12, 15, 15, 12, 15, 15, 60, 60, 60, 60, 80, 60]
            for i, width in enumerate(widths[:len(column_order)]):
                col_letter = chr(65 + i) if i < 26 else f"A{chr(65 + i - 26)}"
                worksheet.set_column(f'{col_letter}:{col_letter}', width)
            
            # Add conditional formatting for priority
            if 'Priority_Level' in available_cols:
                priority_col = column_order.index('Priority_Level')
                worksheet.conditional_format(2, priority_col, len(detailed_df) + 1, priority_col, {
                    'type': 'text',
                    'criteria': 'containing',
                    'value': 'High',
                    'format': workbook.add_format({'bg_color': '#FFE5E5', 'font_color': '#C00000'})
                })
                worksheet.conditional_format(2, priority_col, len(detailed_df) + 1, priority_col, {
                    'type': 'text',
                    'criteria': 'containing',
                    'value': 'Medium',
                    'format': workbook.add_format({'bg_color': '#FFF4E5', 'font_color': '#FF8C00'})
                })
                worksheet.conditional_format(2, priority_col, len(detailed_df) + 1, priority_col, {
                    'type': 'text',
                    'criteria': 'containing',
                    'value': 'Low',
                    'format': workbook.add_format({'bg_color': '#E5F4E5', 'font_color': '#008000'})
                })
        
        except Exception as e:
            logger.warning(f"Failed to create detailed RFM sheet: {e}")
            return
    
    def _create_segments_sheet(
        self,
        writer: pd.ExcelWriter,
        workbook: Any,
        formats: Dict[str, Any],
        rfm_results: Dict[str, Any],
        translations: Dict[str, Any]
    ):
        """Create segments summary sheet."""
        try:
            segment_summary = rfm_results.get('segment_summary', {})
            
            if not segment_summary or not isinstance(segment_summary, dict):
                return
            
            # Convert to DataFrame
            segments_data = []
            for segment_name, data in segment_summary.items():
                if not isinstance(data, dict):
                    continue
                    
                segments_data.append({
                    'Segment': segment_name,
                    'Customer Count': data.get('customer_count', 0),
                    'Total Revenue': data.get('total_revenue', 0),
                    'Avg Revenue per Customer': data.get('avg_revenue_per_customer', 0),
                    'Avg Recency Score': data.get('avg_recency', 0),
                    'Avg Frequency Score': data.get('avg_frequency', 0),
                    'Avg Monetary Score': data.get('avg_monetary', 0),
                })
            
            if not segments_data:
                return
            
            df_segments = pd.DataFrame(segments_data)
            df_segments.to_excel(writer, sheet_name='4_Segments', index=False)
            
            worksheet = writer.sheets['4_Segments']
            
            # Format headers
            for col_num, value in enumerate(df_segments.columns.values):
                worksheet.write(0, col_num, value, formats['header'])
            
            # Set column widths
            worksheet.set_column('A:A', 25)
            worksheet.set_column('B:G', 18)
        except Exception as e:
            logger.warning(f"Failed to create segments sheet: {e}")
            return
    
    def _create_cohorts_sheet(
        self,
        writer: pd.ExcelWriter,
        workbook: Any,
        formats: Dict[str, Any],
        cohort_results: Dict[str, Any],
        translations: Dict[str, Any]
    ):
        """Create cohorts analysis sheet."""
        try:
            retention_matrix = cohort_results.get('retention_matrix')
            
            # Validate retention_matrix is a valid DataFrame
            if retention_matrix is None:
                return
            
            if not isinstance(retention_matrix, pd.DataFrame):
                return
            
            if len(retention_matrix) == 0:
                return
            
            retention_matrix.to_excel(writer, sheet_name='5_Cohorts')
            
            worksheet = writer.sheets['5_Cohorts']
            
            # Format as percentages
            for row in range(1, len(retention_matrix) + 1):
                for col in range(1, len(retention_matrix.columns) + 1):
                    try:
                        value = retention_matrix.iloc[row-1, col-1]
                        if pd.notna(value):
                            worksheet.write(row, col, value, formats['percent'])
                    except Exception:
                        continue
        except Exception as e:
            logger.warning(f"Failed to create cohorts sheet: {e}")
            return
    
    def _create_products_sheet(
        self,
        writer: pd.ExcelWriter,
        workbook: Any,
        formats: Dict[str, Any],
        product_results: Dict[str, Any],
        translations: Dict[str, Any]
    ):
        """Create products analysis sheet."""
        try:
            top_products = product_results.get('top_products_by_revenue', [])
            
            if not top_products or not isinstance(top_products, list):
                return
            
            if len(top_products) == 0:
                return
            
            df_products = pd.DataFrame(top_products)
            
            if len(df_products) == 0:
                return
            
            df_products.to_excel(writer, sheet_name='6_Products', index=False)
            
            worksheet = writer.sheets['6_Products']
            
            # Format headers
            for col_num, value in enumerate(df_products.columns.values):
                worksheet.write(0, col_num, value, formats['header'])
            
            # Set column widths
            worksheet.set_column('A:A', 30)  # product_name
            worksheet.set_column('B:E', 15)  # metrics
        except Exception as e:
            logger.warning(f"Failed to create products sheet: {e}")
            return
    
    def _create_anomalies_sheet(
        self,
        writer: pd.ExcelWriter,
        workbook: Any,
        formats: Dict[str, Any],
        anomaly_results: Dict[str, Any],
        translations: Dict[str, Any]
    ):
        """Create anomalies sheet."""
        try:
            all_anomalies = anomaly_results.get('all_anomalies', [])
            
            if not all_anomalies or not isinstance(all_anomalies, list):
                return
            
            if len(all_anomalies) == 0:
                return
            
            df_anomalies = pd.DataFrame(all_anomalies)
            
            if len(df_anomalies) == 0:
                return
            
            df_anomalies.to_excel(writer, sheet_name='7_Anomalies', index=False)
            
            worksheet = writer.sheets['7_Anomalies']
            
            # Format headers
            for col_num, value in enumerate(df_anomalies.columns.values):
                worksheet.write(0, col_num, value, formats['header'])
            
            worksheet.set_column('A:A', 15)
            worksheet.set_column('B:B', 25)
            worksheet.set_column('C:C', 50)
        except Exception as e:
            logger.warning(f"Failed to create anomalies sheet: {e}")
            return
            worksheet.set_column('D:D', 15)
    
    def _create_data_dictionary(
        self,
        writer: pd.ExcelWriter,
        workbook: Any,
        formats: Dict[str, Any],
        translations: Dict[str, Any]
    ):
        """Create data dictionary sheet."""
        worksheet = workbook.add_worksheet('8_Data_Dictionary')
        
        # Title
        worksheet.merge_range('A1:C1', 'Data Dictionary', formats['title'])
        worksheet.set_row(0, 25)
        
        # Headers
        row = 2
        worksheet.write(row, 0, 'Field Name', formats['header'])
        worksheet.write(row, 1, 'Description', formats['header'])
        worksheet.write(row, 2, 'Type', formats['header'])
        
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 50)
        worksheet.set_column('C:C', 15)
        
        row += 1
        
        # RFM definitions
        definitions = [
            ('Recency (R)', 'Days since last purchase. Lower = more recent. Scored 1-5 (5=best)', 'Score'),
            ('Frequency (F)', 'Number of distinct orders. Higher = more loyal. Scored 1-5 (5=best)', 'Score'),
            ('Monetary (M)', 'Total revenue from customer. Higher = more valuable. Scored 1-5 (5=best)', 'Score'),
            ('RFM Score', 'Combined R+F+M scores to determine segment', 'Composite'),
            ('Customer Segment', '11 segments: Champions, Loyal, At Risk, Lost, etc.', 'Category'),
            ('LTV', 'Customer Lifetime Value - total revenue from customer', 'Currency'),
            ('AOV', 'Average Order Value - mean revenue per order', 'Currency'),
            ('Cohort', 'Group of customers acquired in same period', 'Category'),
            ('Retention Rate', 'Percentage of customers who made repeat purchase', 'Percentage'),
        ]
        
        for field, description, field_type in definitions:
            worksheet.write(row, 0, field, formats['text'])
            worksheet.write(row, 1, description, formats['wrap'])
            worksheet.write(row, 2, field_type, formats['text'])
            worksheet.set_row(row, 30)
            row += 1
    
    def _create_run_log(
        self,
        writer: pd.ExcelWriter,
        workbook: Any,
        formats: Dict[str, Any],
        df_clean: pd.DataFrame,
        validation_report: Dict[str, Any],
        translations: Dict[str, Any]
    ):
        """Create run log sheet."""
        worksheet = workbook.add_worksheet('9_Run_Log')
        
        # Title
        worksheet.merge_range('A1:B1', 'Analysis Run Log', formats['title'])
        worksheet.set_row(0, 25)
        
        row = 2
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:B', 40)
        
        # Metadata
        has_order_date = 'order_date' in list(df_clean.columns) if isinstance(df_clean, pd.DataFrame) and len(df_clean) > 0 else False
        date_range_str = f"{df_clean['order_date'].min()} to {df_clean['order_date'].max()}" if has_order_date else 'N/A'
        
        metadata = [
            ('Report Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('Application', f'{APP_NAME} v{APP_VERSION}'),
            ('Author', 'Omar Rageh'),
            ('Language', self.language.upper()),
            ('Total Rows Analyzed', len(df_clean)),
            ('Total Columns', len(df_clean.columns)),
            ('Date Range', date_range_str),
            ('Data Quality Score', f"{validation_report.get('data_quality', {}).get('overall_score', 0):.1%}" if validation_report else 'N/A'),
        ]
        
        for label, value in metadata:
            worksheet.write(row, 0, label, formats['subheader'])
            worksheet.write(row, 1, str(value), formats['text'])
            row += 1
    
    def _create_financial_analysis_sheet(
        self,
        writer: pd.ExcelWriter,
        workbook: Any,
        formats: Dict[str, Any],
        analysis_results: Dict[str, Any],
        translations: Dict[str, Any]
    ):
        """Create segment financial analysis sheet."""
        try:
            financial_insights = analysis_results.get('financial_insights', {})
            if not financial_insights:
                return
            
            segment_opportunities = financial_insights.get('segment_opportunities', {})
            if not segment_opportunities:
                return
            
            # Create data for each segment
            data_rows = []
            for segment_name, opp in segment_opportunities.items():
                data_rows.append({
                    'Segment': segment_name,
                    'Customer_Count': opp.get('current_customers', 0),
                    'Current_Revenue_SAR': opp.get('current_revenue', 0),
                    'Avg_Revenue_Per_Customer': opp.get('current_avg_per_customer', 0),
                    'Potential_Revenue_Conservative': opp.get('conservative', {}).get('potential_revenue', 0),
                    'Potential_Revenue_Moderate': opp.get('moderate', {}).get('potential_revenue', 0),
                    'Potential_Revenue_Aggressive': opp.get('aggressive', {}).get('potential_revenue', 0),
                    'Revenue_Uplift_Conservative': opp.get('conservative', {}).get('revenue_increase', 0),
                    'Revenue_Uplift_Moderate': opp.get('moderate', {}).get('revenue_increase', 0),
                    'Revenue_Uplift_Aggressive': opp.get('aggressive', {}).get('revenue_increase', 0),
                    'ROI_Conservative_%': opp.get('conservative', {}).get('roi_percentage', 0),
                    'ROI_Moderate_%': opp.get('moderate', {}).get('roi_percentage', 0),
                    'ROI_Aggressive_%': opp.get('aggressive', {}).get('roi_percentage', 0),
                    'Quick_Win_Strategy': ', '.join(opp.get('quick_wins', [])[:2]) if opp.get('quick_wins') else 'No quick wins identified',
                    'Implementation_Timeline': opp.get('timeline', 'Not specified'),
                    'Risk_Level': opp.get('risk_assessment', {}).get('level', 'Unknown'),
                    'Success_Probability': f"{opp.get('risk_assessment', {}).get('success_probability', 0):.0%}"
                })
            
            if not data_rows:
                return
            
            df_financial = pd.DataFrame(data_rows)
            df_financial.to_excel(writer, sheet_name='Financial_Analysis', index=False, startrow=1)
            
            worksheet = writer.sheets['Financial_Analysis']
            
            # Title
            worksheet.merge_range(0, 0, 0, len(df_financial.columns)-1, '💰 Financial Analysis - Revenue Opportunities by Segment', formats['title'])
            
            # Headers
            for col_num, col_name in enumerate(df_financial.columns):
                worksheet.write(1, col_num, col_name, formats['header'])
            
            # Column widths
            worksheet.set_column('A:A', 20)  # Segment
            worksheet.set_column('B:M', 18)  # Numbers
            worksheet.set_column('N:N', 50)  # Quick Win Strategy
            worksheet.set_column('O:Q', 20)  # Timeline, Risk, Probability
            
        except Exception as e:
            logger.warning(f"Failed to create financial analysis sheet: {e}")
            return
    
    def _create_financial_assumptions_sheet(
        self,
        writer: pd.ExcelWriter,
        workbook: Any,
        formats: Dict[str, Any],
        analysis_results: Dict[str, Any],
        translations: Dict[str, Any]
    ):
        """Create financial assumptions documentation sheet."""
        worksheet = workbook.add_worksheet('Financial_Assumptions')
        
        # Title
        worksheet.merge_range('A1:C1', '📋 Financial Assumptions & Methodology', formats['title'])
        worksheet.set_row(0, 25)
        
        row = 2
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:B', 60)
        worksheet.set_column('C:C', 20)
        
        # Headers
        worksheet.write(row, 0, 'Category', formats['header'])
        worksheet.write(row, 1, 'Assumption / Formula', formats['header'])
        worksheet.write(row, 2, 'Value / Method', formats['header'])
        row += 1
        
        # Assumptions
        assumptions = [
            ('Revenue Calculation', 'Based on historical order_total from Salla data', 'Actual data'),
            ('Customer Segmentation', 'RFM Analysis: Recency (days), Frequency (orders), Monetary (SAR)', '11 segments'),
            ('Conservative Scenario', '10-15% revenue increase through basic retention tactics', '10-15% uplift'),
            ('Moderate Scenario', '20-30% revenue increase through active engagement campaigns', '20-30% uplift'),
            ('Aggressive Scenario', '40-60% revenue increase through comprehensive loyalty program', '40-60% uplift'),
            ('Marketing Cost Estimate', '5-10% of potential revenue increase as marketing investment', '5-10% of uplift'),
            ('ROI Calculation', '(Revenue Increase - Marketing Cost) / Marketing Cost * 100%', 'Percentage return'),
            ('Implementation Timeline', 'Based on segment complexity and current customer engagement level', '30-180 days'),
            ('Success Probability', 'Estimated based on segment characteristics and market conditions', '40-85%'),
            ('Data Quality', 'Based on completeness, consistency, and validity of input data', 'Automated score'),
            ('Currency', 'All monetary values in Saudi Riyal (SAR)', 'SAR'),
            ('Analysis Period', 'Based on date range in uploaded Salla export data', 'Actual range'),
        ]
        
        for category, assumption, value in assumptions:
            worksheet.write(row, 0, category, formats['subheader'])
            worksheet.write(row, 1, assumption, formats['wrap'])
            worksheet.write(row, 2, value, formats['text'])
            worksheet.set_row(row, 40)
            row += 1
        
        # Add important notes
        row += 2
        worksheet.merge_range(row, 0, row, 2, 'IMPORTANT NOTES:', formats['subheader'])
        row += 1
        
        notes = [
            '1. All projections are estimates based on historical data and industry benchmarks',
            '2. Actual results will vary based on execution quality, market conditions, and customer response',
            '3. Conservative scenarios have higher success probability but lower returns',
            '4. Aggressive scenarios require significant investment and have higher risk',
            '5. Quick wins should be prioritized for immediate revenue impact',
            '6. Regular monitoring and adjustment of strategies is essential for success',
            '7. Customer engagement metrics should be tracked weekly during implementation'
        ]
        
        for note in notes:
            worksheet.merge_range(row, 0, row, 2, note, formats['wrap'])
            worksheet.set_row(row, 30)
            row += 1
    
    # Helper methods for business explanations
    def _explain_recency(self, days: float) -> str:
        """Explain recency score in business terms."""
        if days <= 30:
            return f"Excellent! Purchased {int(days)} days ago (very recent, highly engaged)"
        elif days <= 90:
            return f"Good. Purchased {int(days)} days ago (recent, still warm lead)"
        elif days <= 180:
            return f"Warning! {int(days)} days since purchase (getting cold, needs attention)"
        elif days <= 365:
            return f"At Risk! {int(days)} days inactive (likely to churn, urgent action needed)"
        else:
            return f"Lost! {int(days)} days inactive (dormant customer, may be unrecoverable)"
    
    def _explain_frequency(self, orders: float) -> str:
        """Explain frequency in business terms."""
        orders = int(orders)
        if orders >= 10:
            return f"Loyal customer! {orders} orders (strong repeat buyer, very valuable)"
        elif orders >= 5:
            return f"Regular customer. {orders} orders (good loyalty, cultivate relationship)"
        elif orders >= 3:
            return f"Repeat buyer. {orders} orders (showing interest, encourage more purchases)"
        elif orders >= 2:
            return f"Second purchase made. {orders} orders (positive sign, nurture carefully)"
        else:
            return f"New customer. {orders} order only (critical to convert to repeat buyer)"
    
    def _explain_monetary(self, amount: float) -> str:
        """Explain monetary value in business terms."""
        if amount >= 5000:
            return f"VIP! Spent {amount:,.0f} SAR (high-value customer, premium treatment essential)"
        elif amount >= 2000:
            return f"High value. Spent {amount:,.0f} SAR (important customer, maintain satisfaction)"
        elif amount >= 1000:
            return f"Good value. Spent {amount:,.0f} SAR (solid customer, upsell opportunities)"
        elif amount >= 500:
            return f"Average. Spent {amount:,.0f} SAR (potential to grow, encourage larger orders)"
        else:
            return f"Low spend. Spent {amount:,.0f} SAR (budget buyer or just starting, grow wallet share)"
    
    def _explain_segment(self, segment: str) -> str:
        """Explain what the segment means in business terms."""
        explanations = {
            'Champions': 'Best customers! Buy frequently, spent most, purchased recently. Reward heavily, ask for referrals.',
            'Loyal Customers': 'Regular buyers who love your brand. High frequency and spend. Keep them engaged with exclusive offers.',
            'Potential Loyalists': 'Recent customers with good frequency. Prime candidates to become Champions with right nurturing.',
            'New Customers': 'Just made first purchase. CRITICAL to convert them to repeat buyers within 30 days or lose them.',
            'Promising': 'Recent buyers who haven\'t bought much yet. Have potential, need encouragement and good experience.',
            'Need Attention': 'Used to buy frequently but haven\'t purchased recently. Win them back NOW before they\'re lost.',
            'About to Sleep': 'Below average recency, frequency and monetary. Fading away, need urgent reactivation campaign.',
            'At Risk': 'Were good customers but slipping away. Need immediate targeted win-back offers.',
            'Hibernating': 'Long time since purchase, low frequency/spend when active. Last chance to recover them.',
            'Lost': 'Haven\'t bought in very long time. Probably gone to competitors. Final recovery attempt or remove from active marketing.',
            'Cannot Lose Them': 'Were your best customers but haven\'t returned recently. High-priority win-back, personal outreach essential.'
        }
        return explanations.get(segment, 'Unknown segment type - review classification rules.')
    
    def _get_recommendation(self, segment: str) -> str:
        """Get specific business recommendation for segment."""
        recommendations = {
            'Champions': '1) Create VIP program with exclusive perks. 2) Ask for testimonials/reviews. 3) Offer referral rewards (SAR 25 for each). 4) Early access to new products.',
            'Loyal Customers': '1) Launch loyalty points (1 pt per SAR, 100 pts = SAR 50 off). 2) Send thank-you note with 10% coupon. 3) Personalized product recommendations. 4) Member-only flash sales.',
            'Potential Loyalists': '1) Welcome series (3 emails over 2 weeks). 2) Second purchase incentive: 15% off + free shipping. 3) Product education content. 4) Bundle offers with 20% discount.',
            'New Customers': '1) IMMEDIATE 20% coupon for 2nd purchase (expires 7 days). 2) WhatsApp follow-up after delivery. 3) Quick 3-question survey (SAR 10 credit). 4) Cross-sell complementary products.',
            'Promising': '1) Flash sale alert (25% off, 24hrs). 2) Free shipping offer (10 days, no minimum). 3) Restock notifications. 4) Show social proof. 5) Highlight payment plans (Tamara/Tabby).',
            'Need Attention': '1) URGENT "We miss you" email with 25% off. 2) Feedback survey (SAR 15 credit). 3) Showcase new arrivals. 4) VIP sale access. 5) Personal WhatsApp from manager.',
            'About to Sleep': '1) "LAST CHANCE" 30% off (48hr timer). 2) Abandoned cart recovery. 3) Free gift with next purchase. 4) 3-email reactivation (15%, 25%, 35% off). 5) Final SMS: 40% off today.',
            'At Risk': '1) Immediate 30% off targeted offer. 2) Personal outreach if high LTV. 3) Survey to understand issues. 4) Highlight improvements made. 5) Limited-time comeback bonus.',
            'Hibernating': '1) Final offer: 40% off to test price sensitivity. 2) Exit survey (why did you leave?). 3) Show major improvements. 4) Retargeting ads. 5) Consider removing from email list.',
            'Lost': '1) One last 50% off (send once only). 2) Brief exit feedback (no incentive). 3) STOP regular marketing (avoid spam). 4) Analyze patterns to prevent future churn. 5) Reallocate budget to active customers.',
            'Cannot Lose Them': '1) URGENT personal call/WhatsApp from owner. 2) Exclusive 35% off + free gift. 3) Understand what went wrong. 4) VIP treatment to rebuild relationship. 5) Regular check-ins after return.'
        }
        return recommendations.get(segment, 'No specific recommendation available. Review segment characteristics and develop appropriate strategy.')
    
    def _get_priority(self, segment: str) -> str:
        """Get business priority level for segment."""
        high_priority = ['Champions', 'Loyal Customers', 'Cannot Lose Them', 'Need Attention']
        medium_priority = ['Potential Loyalists', 'New Customers', 'At Risk', 'About to Sleep']
        
        if segment in high_priority:
            return 'High Priority'
        elif segment in medium_priority:
            return 'Medium Priority'
        else:
            return 'Low Priority'
    
    def _get_expected_action(self, segment: str) -> str:
        """Get immediate next action for segment."""
        actions = {
            'Champions': 'Send VIP invitation email THIS WEEK. Set up WhatsApp VIP group. Prepare birthday tracking system.',
            'Loyal Customers': 'Launch loyalty points program. Send personalized thank-you with 10% coupon valid 7 days.',
            'Potential Loyalists': 'Set up automated welcome series. Create 15% off coupon for 2nd purchase (14-day validity).',
            'New Customers': 'CRITICAL: Send 20% off coupon within 24 hours of first order. Schedule WhatsApp follow-up for day 3.',
            'Promising': 'Create flash sale campaign (25% off, 24hrs). Enable restock notifications for viewed products.',
            'Need Attention': 'URGENT: Send "We miss you" email TODAY with 25% off. Prepare feedback survey with SAR 15 incentive.',
            'About to Sleep': 'LAST CHANCE: Send 30% off with countdown timer (48hrs). Prepare 3-email reactivation sequence.',
            'At Risk': 'Immediate 30% targeted offer. If high LTV, schedule personal outreach call within 48 hours.',
            'Hibernating': 'Send final 40% off attempt. Prepare exit survey. Consider removing from active email list after this.',
            'Lost': 'One final 50% offer (send once). Then STOP marketing to avoid spam complaints. Analyze churn patterns.',
            'Cannot Lose Them': 'HIGHEST PRIORITY: Personal call/WhatsApp from owner/manager TODAY. Prepare exclusive recovery offer.'
        }
        return actions.get(segment, 'Review segment data and develop appropriate immediate action plan.')
