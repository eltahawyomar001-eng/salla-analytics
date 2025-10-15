"""Upload page for Salla data file."""

import streamlit as st
import pandas as pd
from pathlib import Path
import logging
from io import BytesIO
from typing import Dict, Any

from app.ui.components import get_translator, show_info_banner, format_number
from app.ingestion.reader import XLSXReader
from app.ingestion.mapper import ColumnMapper
from app.ingestion.validators import DataValidator
from app.ingestion.aggregator import DataAggregator
from app.analytics.kpis import KPICalculator
from app.analytics.rfm import RFMAnalyzer
from app.analytics.cohorts import CohortAnalyzer
from app.analytics.products import ProductAnalyzer
from app.analytics.anomalies import AnomalyDetector

logger = logging.getLogger(__name__)

def _update_mapping(field: str, value: str | None):
    """Update mapping in session state when selectbox changes."""
    if value:
        st.session_state.mappings[field] = value
    elif field in st.session_state.mappings:
        del st.session_state.mappings[field]

def render_upload_page():
    """Render the data upload and processing page."""
    language = st.session_state.language
    t = get_translator(language)

    st.title(t['navigation']['upload'])
    st.markdown(t['upload']['description'])
    
    # If data is already loaded and analysis is complete, show success and tell user to use navigation
    if st.session_state.get('data_loaded', False):
        st.success("✅ **Data analysis complete!**")
        st.balloons()
        st.info("👈 **Use the navigation menu on the left** to view your analysis results (Executive Summary, Financial Insights, Customers, etc.)")
        st.markdown("---")
        st.info("📊 Navigate to **Executive Summary**, **Financial Insights**, **Customers (RFM)**, or other pages to explore your data.")
        
        # Show which analyses are available
        st.markdown("### 📈 Available Analysis:")
        cols = st.columns(3)
        with cols[0]:
            st.markdown("- ✅ Executive Summary\n- ✅ Financial Insights")
        with cols[1]:
            st.markdown("- ✅ Customer Segmentation (RFM)\n- ✅ Cohort Analysis")
        with cols[2]:
            st.markdown("- ✅ Anomaly Detection\n- ✅ Product Analysis")
        
        # Option to upload a new file
        st.markdown("---")
        if st.button("📤 Upload New File", type="secondary"):
            # Clear session state for new upload
            for key in list(st.session_state.keys()):
                if key not in ['language', 'lang_selector']:
                    del st.session_state[key]
            st.rerun()
        return  # Don't render the upload form again

    # File upload
    uploaded_file = st.file_uploader(
        t['upload']['choose_file'],
        type=['xlsx', 'xls'],
        help=t['upload']['file_requirements']
    )

    if uploaded_file is not None:
        try:
            # Show upload success banner
            show_info_banner(
                t['upload']['file_uploaded'].format(filename=uploaded_file.name),
                banner_type='success',
                language=language
            )
            
            # Step 1: Read file (only once per file)
            if 'df_raw' not in st.session_state or st.session_state.get('current_file') != uploaded_file.name:
                with st.spinner(t['upload']['reading_file']):
                    reader = XLSXReader()
                    # Save uploaded file temporarily
                    import tempfile
                    import os
                    
                    tmp_path = None
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_path = tmp_file.name
                        
                        df_raw, metadata = reader.read_excel_file(tmp_path)
                        
                        # CRITICAL: Clear all old state when new file is uploaded
                        st.session_state.df_raw = df_raw
                        st.session_state.metadata = metadata
                        st.session_state.current_file = uploaded_file.name
                        
                        # Clear old mappings and analysis results
                        if 'mappings' in st.session_state:
                            del st.session_state.mappings
                        if 'mapping_file' in st.session_state:
                            del st.session_state.mapping_file
                        if 'df_clean' in st.session_state:
                            del st.session_state.df_clean
                        if 'analysis_results' in st.session_state:
                            st.session_state.analysis_results = {}
                        # Clear data_loaded flag when new file uploaded
                        st.session_state.data_loaded = False
                        
                        st.success(t['upload']['file_read_success'].format(
                            rows=format_number(len(df_raw), language, decimals=0),
                            columns=format_number(len(df_raw.columns), language, decimals=0)
                        ))
                    finally:
                        # Clean up temp file
                        if tmp_path and os.path.exists(tmp_path):
                            try:
                                os.unlink(tmp_path)
                            except (PermissionError, OSError):
                                # File might still be in use, try again later
                                pass
            else:
                # Use cached dataframe
                df_raw = st.session_state.df_raw
            
            # Show preview
            with st.expander(t['upload']['preview_data'], expanded=False):
                st.dataframe(df_raw.head(10))
            
            # Step 2: Column mapping
            st.markdown(f"## {t['upload']['step_mapping']}")
            
            # Initialize mappings in session state if not already done OR if file changed
            # CRITICAL: Clear old mappings when a new file is uploaded!
            if ('mappings' not in st.session_state or 
                len(st.session_state.mappings) == 0 or 
                st.session_state.get('mapping_file') != uploaded_file.name):
                
                mapper = ColumnMapper()
                
                # Try auto-detection (only once per file)
                with st.spinner(t['upload']['detecting_columns']):
                    auto_mappings, confidence_scores = mapper.auto_detect_columns(df_raw)
                    
                    # Calculate average confidence for required fields only
                    required_fields = ['order_id', 'order_date', 'customer_id', 'order_total']
                    required_confidences = [confidence_scores.get(f, 0) for f in required_fields]
                    avg_confidence = sum(required_confidences) / len(required_confidences) if required_confidences else 0
                    
                    # Store in session state
                    st.session_state.mappings = auto_mappings
                    st.session_state.confidence_scores = confidence_scores
                    st.session_state.mapping_file = uploaded_file.name  # Track which file these mappings are for
                    
                    if avg_confidence >= 0.8:
                        st.success(t['upload']['auto_detect_success'].format(
                            confidence=format_number(avg_confidence * 100, language, decimals=0)
                        ))
                    else:
                        st.warning(t['upload']['auto_detect_partial'].format(
                            confidence=format_number(avg_confidence * 100, language, decimals=0)
                        ))
            
            # Show detected mappings
            st.markdown(f"### {t['upload']['detected_mappings']}")
            
            # Show what was auto-detected
            if st.session_state.mappings:
                detected_fields = [k for k, v in st.session_state.mappings.items() if v]
                required_fields_list = ['order_id', 'order_date', 'customer_id', 'order_total']
                missing_required = [f for f in required_fields_list if f not in detected_fields]
                
                st.success(f"✅ Auto-detected {len(detected_fields)} fields: {', '.join(detected_fields)}")
                
                if missing_required:
                    st.warning(f"⚠️ Missing required fields: {', '.join(missing_required)}")
                    
                # Debug: Show all mappings
                with st.expander("🔍 Debug: All Auto-Detected Mappings", expanded=False):
                    for field, column in st.session_state.mappings.items():
                        confidence = st.session_state.confidence_scores.get(field, 0)
                        if column:
                            st.write(f"✅ {field}: '{column}' (confidence: {confidence:.0%})")
                        else:
                            st.write(f"❌ {field}: NOT DETECTED")
            
            # Allow manual adjustment
            available_columns = [''] + list(df_raw.columns)
            
            # Required fields
            st.markdown(f"**{t['upload']['required_fields']}**")
            
            required_fields = {
                'order_id': t['upload']['order_id'],
                'order_date': t['upload']['order_date'],
                'customer_id': t['upload']['customer_id'],
                'order_total': t['upload']['order_total']
            }
            
            col1, col2 = st.columns(2)
            
            for idx, (field, label) in enumerate(required_fields.items()):
                target_col = col1 if idx % 2 == 0 else col2
                with target_col:
                    current_mapping = st.session_state.mappings.get(field, '')
                    # Use on_change callback instead of direct assignment
                    st.selectbox(
                        label,
                        options=available_columns,
                        index=available_columns.index(current_mapping) if current_mapping in available_columns else 0,
                        key=f"map_{field}",
                        help=f"Confidence: {st.session_state.confidence_scores.get(field, 0):.0%}" if field in st.session_state.get('confidence_scores', {}) else None,
                        on_change=lambda f=field: _update_mapping(f, st.session_state.get(f"map_{f}"))
                    )
            
            # Optional fields
            with st.expander(t['upload']['optional_fields'], expanded=False):
                optional_fields = {
                    'order_status': t['upload']['order_status'],
                    'product_name': t['upload']['product_name'],
                    'category': t['upload']['category'],
                    'quantity': t['upload']['quantity'],
                    'unit_price': t['upload']['unit_price'],
                    'customer_name': t['upload']['customer_name'],
                    'customer_email': t['upload']['customer_email'],
                    'customer_phone': t['upload']['customer_phone'],
                    'currency': t['upload']['currency']
                }
                
                col1, col2 = st.columns(2)
                
                for idx, (field, label) in enumerate(optional_fields.items()):
                    target_col = col1 if idx % 2 == 0 else col2
                    with target_col:
                        current_mapping = st.session_state.mappings.get(field, '')
                        # Use on_change callback instead of direct assignment
                        st.selectbox(
                            label,
                            options=available_columns,
                            index=available_columns.index(current_mapping) if current_mapping in available_columns else 0,
                            key=f"map_{field}",
                            help=f"Confidence: {st.session_state.confidence_scores.get(field, 0):.0%}" if field in st.session_state.get('confidence_scores', {}) else None,
                            on_change=lambda f=field: _update_mapping(f, st.session_state.get(f"map_{f}"))
                        )
            
            # Step 3: Validate and process
            # Track current file for aggregation approval
            current_file = st.session_state.get('current_file', uploaded_file.name)
            st.session_state.current_file = current_file
            
            aggregation_approved_key = f"agg_approved_{current_file}"
            
            # Check if we need to show aggregation approval UI first
            # Quick pre-check: does data need aggregation and is it not yet approved?
            needs_aggregation_check = False
            aggregator = DataAggregator()
            
            # Only do this check if Process button is clicked and aggregation not yet approved
            should_process = st.button(t['upload']['process_button'], type="primary", use_container_width=True)
            
            if should_process and aggregation_approved_key not in st.session_state:
                # Quick check if data needs aggregation before full processing
                mapper = ColumnMapper()
                rename_dict = {v: k for k, v in st.session_state.mappings.items() if v}
                df_temp = st.session_state.df_raw.rename(columns=rename_dict)
                detection = aggregator.detect_data_level(df_temp, st.session_state.mappings)
                
                if detection['requires_aggregation']:
                    # Show aggregation approval UI
                    st.info(f"📦 **Line-Item Data Detected** ({detection['confidence']*100:.0f}% confidence)")
                    st.info(f"**Indicators**: {', '.join(detection['indicators'])}")
                    
                    with st.expander("🔄 Data Aggregation Required", expanded=True):
                        aggregation_help = "\n".join([
                            "Your data appears to be at **line-item level** (one row per product/item).",
                            "The analysis needs **order-level data** (one row per order).",
                            "",
                            "**Aggregation will:**",
                            "- Group items into orders (by customer + date)",
                            "- Sum item prices to get order totals",
                            "- Count items per order",
                            "- Preserve customer and date information",
                        ])
                        st.markdown(aggregation_help)

                        # Use a callback function to set the approval flag only
                        def approve_aggregation():
                            st.session_state[aggregation_approved_key] = True
                            logger.info(f"✅ Aggregation approved for {current_file}")

                        st.button(
                            "✅ Approve Aggregation",
                            type="primary",
                            key="aggregate_btn",
                            on_click=approve_aggregation
                        )
                    
                    st.info("👆 Click above to proceed with aggregation")
                    # Don't process yet - wait for approval
                    needs_aggregation_check = True
            
            # Now process if button clicked and aggregation approval isn't needed
            if should_process and not needs_aggregation_check:
                logger.info("🔘 PROCESS DATA BUTTON CLICKED - starting processing")
                # Use the dataframe from session state (guaranteed to have ALL rows)
                process_data(st.session_state.df_raw, st.session_state.mappings, t, language)
        
        except Exception as e:
            logger.error(f"Error processing upload: {e}", exc_info=True)
            st.error(t['errors']['processing_error'].format(error=str(e)))
            st.info(t['errors']['check_file_format'])
    
    else:
        # Show instructions when no file uploaded
        st.info(t['upload']['no_file'])
        
        # Show requirements
        with st.expander(t['upload']['requirements_title'], expanded=True):
            st.markdown(t['upload']['requirements_list'])

def process_data(df_raw: pd.DataFrame, mappings: Dict[str, str], t: Dict[str, Any], language: str):
    """Process the uploaded data through validation, cleaning, and analysis."""

    logger.info("🚀 PROCESS_DATA CALLED - Starting data processing")
    logger.info("   DataFrame: %s rows x %s columns", len(df_raw), len(df_raw.columns))
    logger.info("   Mappings: %s", mappings)
    st.info("🚀 **DEBUG**: Process Data function called - starting validation...")

    progress_panel = st.expander("🧩 Debug: Process Data Progress", expanded=True)

    def log_progress(step: str, **details: Any) -> None:
        entry = {"step": step}
        entry.update(details)
        progress_panel.write(entry)

    log_progress("start", df_raw_shape=df_raw.shape, mappings=mappings)

    try:
        log_progress("mapping_validation", status="validating mappings and data")

        # Validate mappings
        mapper = ColumnMapper()
        
        with st.spinner(t['upload']['validating_mappings']):
            validation_result = mapper.validate_mappings(df_raw, mappings)
            
            # Show warnings (like using phone as customer_id)
            for warning in validation_result.get('warnings', []):
                st.info(f"ℹ️ {warning}")
            
            is_valid = validation_result['is_valid']
            
            if not is_valid:
                st.error(t['upload']['invalid_mappings'])
                for error in validation_result.get('errors', []):
                    st.error(f"• {error}")
                return
            
            st.success(t['upload']['mappings_valid'])
        
        # Apply mappings
        rename_dict = {v: k for k, v in mappings.items() if v}
        df_mapped = df_raw.rename(columns=rename_dict)
        
        # Debug: Show actual mapping transformation
        with st.expander("🔍 Debug: Column Mapping Applied", expanded=False):
            st.write("**Mappings Dictionary:**")
            for canonical, original in mappings.items():
                if original:
                    st.write(f"   {original} → {canonical}")
            st.write("\n**Columns Before Mapping:**", list(df_raw.columns[:10]))
            st.write("**Columns After Mapping:**", list(df_mapped.columns[:10]))
        
        # Debug info
        st.info(f"📊 **Data Summary**: {len(df_raw):,} rows loaded from file → {len(df_mapped):,} rows after mapping")
        
        # Check if data needs aggregation (line-item → order level)
        aggregator = DataAggregator()
        
        with st.spinner("🔍 Analyzing data structure..."):
            detection = aggregator.detect_data_level(df_mapped, mappings)
            
            if detection['requires_aggregation']:
                logger.info(f"📦 Line-item data detected - requires aggregation")
                log_progress(
                    "aggregation_required",
                    status="waiting for user approval",
                    confidence=detection['confidence'],
                    indicators=detection['indicators'],
                )
                
                # Check if user already approved aggregation
                current_file = st.session_state.get('current_file', 'unknown')
                aggregation_approved_key = f"agg_approved_{current_file}"
                
                if aggregation_approved_key not in st.session_state:
                    # Show detection info
                    st.info(f"📦 **Line-Item Data Detected** ({detection['confidence']*100:.0f}% confidence)")
                    st.info(f"**Indicators**: {', '.join(detection['indicators'])}")
                    
                    # Show aggregation options
                    with st.expander("🔄 Data Aggregation Required", expanded=True):
                        aggregation_help = "\n".join([
                            "Your data appears to be at **line-item level** (one row per product/item).",
                            "The analysis needs **order-level data** (one row per order).",
                            "",
                            "**Aggregation will:**",
                            "- Group items into orders (by customer + date)",
                            "- Sum item prices to get order totals",
                            "- Count items per order",
                            "- Preserve customer and date information",
                        ])
                        st.markdown(aggregation_help)

                        if st.button("✅ Aggregate to Order Level", type="primary", key="aggregate_btn"):
                            logger.info("🔘 AGGREGATE BUTTON CLICKED - setting approval flag")
                            st.session_state[aggregation_approved_key] = True
                            # Set auto-process flag so process_data runs automatically after rerun
                            auto_process_key = f"auto_process_{current_file}"
                            st.session_state[auto_process_key] = True
                            st.rerun()
                    
                    st.info("👆 Click above to proceed with aggregation")
                    return
                
                # User has approved aggregation - perform it now
                logger.info(f"🔄 Aggregation approved - proceeding with aggregation")
                log_progress("aggregation", status="aggregating data")
                with st.spinner("🔄 Aggregating line items to orders..."):
                    try:
                        df_aggregated = aggregator.aggregate_to_orders(df_mapped, mappings)
                        agg_summary = aggregator.get_aggregation_summary(df_mapped, df_aggregated)
                        
                        st.success(f"✅ Aggregated {agg_summary['original_rows']:,} line items → {agg_summary['aggregated_rows']:,} orders")
                        st.info(f"📊 Avg {agg_summary['avg_items_per_order']:.1f} items per order")
                        
                        # Use aggregated data for further processing
                        df_mapped = df_aggregated
                        
                    except Exception as e:
                        logger.error(f"Aggregation failed: {e}", exc_info=True)
                        st.error(f"❌ Aggregation failed: {str(e)}")
                        st.info("**Tip**: Make sure your data has customer_id, order_date, and price columns")
                        return
            else:
                st.success(f"✅ **Order-Level Data Detected** - No aggregation needed")
        
        log_progress("data_validation", status="validating dataframe")

        # Validate data
        validator = DataValidator()
        
        with st.spinner(t['upload']['validating_data']):
            try:
                validation_report = validator.validate_dataframe(df_mapped, mappings)
                
                # Store currency info in session state for analysis
                if 'currency_info' in validation_report:
                    st.session_state.currency_info = validation_report['currency_info']
                    logger.info(f"💰 Currency info stored: {validation_report['currency_info']}")
                
                # Show critical errors first
                if validation_report['errors']:
                    st.error("❌ **Critical Validation Issues:**")
                    for error in validation_report['errors'][:10]:  # Show first 10 errors
                        st.error(f"• {error}")
                    
                    if len(validation_report['errors']) > 10:
                        st.info(f"...and {len(validation_report['errors']) - 10} more errors")
                    
                    # If too many errors, stop here
                    if len(validation_report['errors']) > 20:
                        st.error("🛑 **Too many validation errors. Please check your data format.**")
                        st.info("**Suggestions:**")
                        suggestions = "\n".join([
                            "- Make sure date columns are in a recognizable format (YYYY-MM-DD, DD/MM/YYYY, etc.)",
                            "- Ensure numeric columns contain valid numbers",
                            "- Check that required fields (order_id, customer_id, order_total) are not empty",
                            "- Verify the data is an e-commerce export with transactional data",
                        ])
                        st.markdown(suggestions)
                        return
                
                # Show warnings
                if validation_report.get('warnings'):
                    with st.expander(f"⚠️ Warnings ({len(validation_report['warnings'])})", expanded=False):
                        for warning in validation_report['warnings'][:10]:
                            st.warning(f"• {warning}")
                        if len(validation_report['warnings']) > 10:
                            st.info(f"...and {len(validation_report['warnings']) - 10} more warnings")
                
                # Show quality score
                overall_quality = validation_report.get('data_quality', {})
                if overall_quality:
                    # Calculate average null percentage
                    null_percentages = [q.get('null_percentage', 0) for q in overall_quality.values()]
                    avg_completeness = 100 - (sum(null_percentages) / len(null_percentages) if null_percentages else 0)
                    
                    if avg_completeness >= 90:
                        st.success(f"✅ Data Quality: Excellent ({avg_completeness:.1f}% complete)")
                    elif avg_completeness >= 70:
                        st.info(f"ℹ️ Data Quality: Good ({avg_completeness:.1f}% complete)")
                    else:
                        st.warning(f"⚠️ Data Quality: Fair ({avg_completeness:.1f}% complete)")
                
            except Exception as e:
                logger.error(f"Error during validation: {e}", exc_info=True)
                st.error(f"❌ Validation failed: {str(e)}")
                st.info("**Debug Info:** Error occurred while validating data structure")
                return
        
        log_progress("cleaning", status="cleaning data")

        # Clean data
        with st.spinner(t['upload']['cleaning_data']):
            try:
                df_clean, cleaning_summary = validator.clean_dataframe(
                    df_mapped, 
                    mappings,
                    already_mapped=True  # Columns already renamed to canonical names
                )
                
                rows_removed = cleaning_summary['removed_rows']
                if rows_removed > 0:
                    st.info(f"🧹 Removed {rows_removed:,} invalid rows")
                    
                    # Show cleaning steps
                    if cleaning_summary.get('cleaning_steps'):
                        with st.expander("Show cleaning details", expanded=False):
                            for step in cleaning_summary['cleaning_steps']:
                                st.text(f"• {step}")
                
                st.success(f"✅ Cleaned data ready: {len(df_clean):,} rows")
                
                # Debug: Show what's being passed to analysis
                st.info(f"🔬 **Starting Analysis**: Processing {len(df_clean):,} rows × {len(df_clean.columns)} columns")
                
            except Exception as e:
                logger.error(f"Error during cleaning: {e}", exc_info=True)
                st.error(f"❌ Cleaning failed: {str(e)}")
                st.info("**Debug Info:** Error occurred while cleaning data")
                st.info("**Tip:** Try processing the data anyway by skipping cleaning (this feature coming soon)")
                return
        
        # Store cleaned data
        st.session_state.df_clean = df_clean
        st.session_state.validation_report = validation_report
        
        # Debug: Show columns before analysis
        with st.expander("🔍 Debug: Columns Before Analysis", expanded=False):
            st.write(f"**Total columns**: {len(df_clean.columns)}")
            st.write(f"**Column names**: {list(df_clean.columns)}")
            required = ['order_date', 'customer_id', 'order_total']
            st.write(f"**Required columns present**: {[col for col in required if col in df_clean.columns]}")
            st.write(f"**Required columns missing**: {[col for col in required if col not in df_clean.columns]}")
        
        log_progress("analysis", status="running analysis")

        # Run analysis
        run_analysis(df_clean, t, language)
        
        # Analysis is complete and data_loaded is set to True
        # The natural page flow will handle showing the success message
        # No need to call st.rerun() - the page will render properly on next interaction
        
    except Exception as e:
        logger.error(f"Error in data processing: {e}", exc_info=True)
        log_progress("error", error=str(e))
        st.error(t['errors']['processing_error'].format(error=str(e)))

def run_analysis(df: pd.DataFrame, t: Dict[str, Any], language: str):
    """Run all analysis modules on the clean data.
    
    Args:
        df: Clean dataframe
        t: Translations
        language: Language code
    """
    st.markdown(f"## {t['upload']['running_analysis']}")
    
    # Use a container for progress elements so they can be cleared
    progress_container = st.container()
    
    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()
    
    try:
        # Debug: Verify dataframe size at start of analysis
        st.write(f"**Analysis Input**: {len(df):,} rows × {len(df.columns)} columns")
        
        # Check for required columns
        required_cols = ['order_date', 'customer_id', 'order_total']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            st.error(f"❌ Missing required columns for analysis: {', '.join(missing_cols)}")
            with st.expander("🔍 Debug: Available Columns", expanded=True):
                st.write("**Columns in dataframe:**")
                st.write(list(df.columns))
                st.write("\n**Required columns:**")
                st.write(required_cols)
                st.write("\n**Missing columns:**")
                st.write(missing_cols)
            logger.error(f"Missing required columns: {missing_cols}. Available: {list(df.columns)}")
            return
        
        # Show date range safely
        try:
            min_date = df['order_date'].min()
            max_date = df['order_date'].max()
            st.write(f"**Date range**: {min_date} to {max_date}")
        except Exception as e:
            st.warning(f"⚠️ Could not determine date range: {e}")
        
        # Show customer count
        try:
            unique_customers = df['customer_id'].nunique()
            st.write(f"**Unique customers**: {unique_customers:,}")
        except Exception as e:
            st.warning(f"⚠️ Could not count customers: {e}")
        
        # Show revenue
        try:
            total_revenue = df['order_total'].sum()
            # Get currency from session state if available
            currency_display = ""
            if 'currency_info' in st.session_state:
                currency = st.session_state.currency_info.get('default_currency')
                if currency:
                    currency_display = f"{currency} "
            st.write(f"**Total revenue**: {currency_display}{total_revenue:,.2f}")
        except Exception as e:
            st.warning(f"⚠️ Could not calculate revenue: {e}")
        
        # 1. KPIs
        status_text.text(t['upload']['analyzing_kpis'])
        try:
            # Get currency from validation results, or use None for generic
            currency = None
            if 'currency_info' in st.session_state:
                currency = st.session_state.currency_info.get('default_currency')
            logger.info(f"💰 Using currency for KPIs: {currency}")
            
            kpi_calc = KPICalculator()
            kpis = kpi_calc.calculate_all_kpis(df, currency=currency)
            st.session_state.analysis_results['kpis'] = kpis
            progress_bar.progress(0.2)
        except Exception as e:
            logger.error(f"KPI calculation failed: {e}", exc_info=True)
            st.error(f"❌ KPI calculation failed: {str(e)}")
            st.session_state.analysis_results['kpis'] = {}
            progress_bar.progress(0.2)
        
        # 2. RFM
        status_text.text(t['upload']['analyzing_rfm'])
        try:
            rfm_analyzer = RFMAnalyzer()
            rfm_df = rfm_analyzer.calculate_rfm_scores(df)
            
            # Get segment summary and heatmap data
            segment_summary = rfm_analyzer.get_segment_summary(rfm_df)
            heatmap_data = rfm_analyzer.get_rfm_heatmap_data(rfm_df)
            
            # Store complete RFM results
            st.session_state.analysis_results['rfm'] = {
                'rfm_data': rfm_df,
                'segment_summary': segment_summary,
                'heatmap_data': heatmap_data
            }
            progress_bar.progress(0.4)
        except Exception as e:
            logger.error(f"RFM analysis failed: {e}", exc_info=True)
            st.error(f"❌ RFM analysis failed: {str(e)}")
            st.session_state.analysis_results['rfm'] = {}
            progress_bar.progress(0.4)
        
        # 3. Cohorts
        status_text.text(t['upload']['analyzing_cohorts'])
        try:
            cohort_analyzer = CohortAnalyzer()
            cohort_results = cohort_analyzer.perform_cohort_analysis(df)
            st.session_state.analysis_results['cohorts'] = cohort_results
            progress_bar.progress(0.6)
        except Exception as e:
            logger.error(f"Cohort analysis failed: {e}", exc_info=True)
            st.error(f"❌ Cohort analysis failed: {str(e)}")
            st.session_state.analysis_results['cohorts'] = {}
            progress_bar.progress(0.6)
        
        # 4. Products
        status_text.text(t['upload']['analyzing_products'])
        product_analyzer = ProductAnalyzer()
        try:
            product_results = product_analyzer.analyze_products(df)
            st.session_state.analysis_results['products'] = product_results
        except Exception as e:
            logger.warning(f"Product analysis skipped: {e}")
            st.session_state.analysis_results['products'] = {
                'product_performance': {},
                'category_analysis': {'available': False},
                'market_basket': {'available': False},
                'lifecycle_metrics': {'available': False},
                'top_products': {},
                'summary_stats': {},
                'total_products': 0
            }
            st.info("ℹ️ Product analysis skipped - no product data available in file")
        progress_bar.progress(0.8)
        
        # 5. Anomalies
        status_text.text(t['upload']['detecting_anomalies'])
        anomaly_detector = AnomalyDetector()
        try:
            anomaly_results = anomaly_detector.detect_anomalies(df)
            st.session_state.analysis_results['anomalies'] = anomaly_results
        except Exception as e:
            logger.warning(f"Anomaly detection failed: {e}")
            st.session_state.analysis_results['anomalies'] = {
                'revenue_anomalies': [],
                'order_anomalies': [],
                'summary': {'total_anomalies': 0}
            }
        progress_bar.progress(1.0)
        
        # Mark data as loaded
        st.session_state.data_loaded = True
        logger.info(f"✅ data_loaded flag set to True. Analysis completed successfully.")
        
        status_text.empty()
        progress_bar.empty()
        
        # Don't show any UI here - let the parent function handle it
        # Just set the flag and return
        
    except Exception as e:
        logger.error(f"Error in analysis: {e}", exc_info=True)
        status_text.empty()
        progress_bar.empty()
        st.error(t['errors']['analysis_error'].format(error=str(e)))