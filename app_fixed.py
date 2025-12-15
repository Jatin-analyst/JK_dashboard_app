# -*- coding: utf-8 -*-
"""
Air Quality vs Middle-Class Income Dashboard - DEPLOYMENT READY VERSION

A Streamlit application for exploratory analysis of relationships between 
air quality indicators, respiratory hospitalization burden, and economic stress indicators.

This version includes comprehensive error handling for Streamlit Cloud deployment.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, date
import sys
import os

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def safe_import():
    """Safely import custom modules with error handling."""
    try:
        from data.real_data_processor import RealDataProcessor
        from ui.sidebar_filters import create_sidebar_filters
        from ui.dashboard_layout import create_dashboard_layout
        return True, RealDataProcessor, create_sidebar_filters, create_dashboard_layout
    except ImportError as e:
        st.error("Error importing modules: {}. Please ensure all dependencies are installed.".format(str(e)))
        return False, None, None, None

@st.cache_data(show_spinner=True, ttl=3600)  # Cache for 1 hour
def load_data_safe():
    """Load and cache the real dataset with comprehensive error handling."""
    try:
        success, RealDataProcessor, _, _ = safe_import()
        if not success:
            return None, None
            
        with st.spinner("Loading and processing air quality data..."):
            processor = RealDataProcessor()
            merged_data = processor.create_comprehensive_dataset()
            
            if merged_data is None or len(merged_data) == 0:
                st.error("No data could be loaded. Please check data files.")
                return None, None
            
            # Optimize data types for better performance
            merged_data = optimize_data_types_safe(merged_data)
            
        return merged_data, processor
    except Exception as e:
        st.error("Error loading data: {}".format(str(e)))
        return None, None

def optimize_data_types_safe(df):
    """Safely optimize DataFrame data types for better performance."""
    try:
        optimized_df = df.copy()
        
        # Convert float64 to float32 where appropriate
        float_cols = optimized_df.select_dtypes(include=['float64']).columns
        for col in float_cols:
            try:
                if optimized_df[col].max() < 1e6:  # Safe range for float32
                    optimized_df[col] = optimized_df[col].astype('float32')
            except:
                continue
        
        # Convert int64 to smaller int types where appropriate
        int_cols = optimized_df.select_dtypes(include=['int64']).columns
        for col in int_cols:
            try:
                col_max = optimized_df[col].max()
                col_min = optimized_df[col].min()
                
                if col_min >= 0 and col_max <= 255:
                    optimized_df[col] = optimized_df[col].astype('uint8')
                elif col_min >= -128 and col_max <= 127:
                    optimized_df[col] = optimized_df[col].astype('int8')
                elif col_min >= 0 and col_max <= 65535:
                    optimized_df[col] = optimized_df[col].astype('uint16')
                elif col_min >= -32768 and col_max <= 32767:
                    optimized_df[col] = optimized_df[col].astype('int16')
            except:
                continue
        
        return optimized_df
    except Exception as e:
        st.warning("Data optimization failed: {}".format(str(e)))
        return df

def create_fallback_dashboard(data):
    """Create a simple fallback dashboard when main dashboard fails."""
    st.title("🌬️ Air Quality Dashboard (Fallback Mode)")
    
    st.warning("""
    **⚠️ DISCLAIMER**: This dashboard is for reference and exploratory analysis only. 
    It makes no medical claims or predictions.
    """)
    
    if data is not None and len(data) > 0:
        st.subheader("📋 Data Overview")
        st.info("Dataset shape: {:,} rows, {} columns".format(data.shape[0], data.shape[1]))
        
        # Safe data display
        try:
            display_data = data.head(10)
            st.dataframe(display_data, use_container_width=True)
        except Exception as e:
            st.error("Could not display data: {}".format(str(e)))
        
        # Basic statistics
        st.subheader("📊 Basic Statistics")
        try:
            numeric_data = data.select_dtypes(include=[np.number])
            if len(numeric_data.columns) > 0:
                st.dataframe(numeric_data.describe(), use_container_width=True)
            else:
                st.info("No numeric columns available for statistics")
        except Exception as e:
            st.warning("Statistics calculation failed: {}".format(str(e)))
    else:
        st.error("❌ No data available for display")

def main():
    """Main application entry point with comprehensive error handling."""
    st.set_page_config(
        page_title="Air Quality vs Income Dashboard",
        page_icon="🌬️",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/your-repo/air-quality-dashboard',
            'Report a bug': 'https://github.com/your-repo/air-quality-dashboard/issues',
            'About': """
            # Air Quality vs Income Dashboard
            
            This dashboard provides exploratory analysis of relationships between 
            air quality indicators, respiratory hospitalization burden, and economic stress indicators.
            
            **Version:** 1.0.0  
            **Data Sources:** Real air quality measurements from Indian cities  
            **Disclaimer:** For reference and research purposes only
            """
        }
    )
    
    # Add custom CSS for better UI
    st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        border: 1px solid #e1e5e9;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    }
    .stAlert {
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    .stSpinner {
        text-align: center;
    }
    .stProgress .st-bo {
        background-color: #ff6b6b;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
    
    # Load data with progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    status_text.text("Initializing data loader...")
    progress_bar.progress(10)
    
    data, processor = load_data_safe()
    progress_bar.progress(50)
    
    if data is not None:
        status_text.text("Data loaded successfully! {} records available.".format(len(data)))
        progress_bar.progress(100)
        
        # Clear progress indicators after a short delay
        import time
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
    else:
        progress_bar.empty()
        status_text.empty()
    
    if data is None:
        st.error("Failed to load data. Please check that the required CSV files exist in the 'data' directory.")
        st.info("""
        Required files:
        - data/city_day.csv (real air quality data)
        - data/station_day.csv (station-level data)
        - data/stations.csv (station information)
        
        The system generates correlated health and economic data based on real air quality measurements.
        """)
        return
    
    # Try to create sidebar filters with comprehensive error handling
    try:
        success, _, create_sidebar_filters, create_dashboard_layout = safe_import()
        if not success:
            create_fallback_dashboard(data)
            return
            
        # Show filter application progress
        filter_progress = st.progress(0)
        filter_status = st.empty()
        
        filter_status.text("🎛️ Initializing filters...")
        filter_progress.progress(25)
        
        with st.spinner("Applying filters..."):
            filtered_data, filter_summary = create_sidebar_filters(data)
            
        filter_progress.progress(75)
        filter_status.text("✅ Filters applied successfully!")
        
        # Show filter performance info
        if filter_summary and 'error' not in filter_summary:
            retention_rate = filter_summary.get('retention_rate', 1.0)
            filtered_count = filter_summary.get('filtered_records', 0)
            
            if retention_rate < 0.01:  # Less than 1% data retained
                st.error("Filters are extremely restrictive ({:.2%} data retained, {:,} records). Please reset or relax filters.".format(retention_rate, filtered_count))
            elif retention_rate < 0.1:  # Less than 10% data retained
                st.warning("Current filters are very restrictive ({:.1%} data retained, {:,} records). Consider relaxing some filters for better analysis.".format(retention_rate, filtered_count))
            elif retention_rate < 0.5:  # Less than 50% data retained
                st.info("Filters have significantly reduced the dataset ({:.1%} retained, {:,} records). Results may be limited.".format(retention_rate, filtered_count))
            else:
                st.success("Filters applied successfully! Showing {:,} records ({:.1%} of original data).".format(filtered_count, retention_rate))
        
        filter_progress.progress(100)
        
        # Clear progress indicators
        import time
        time.sleep(0.5)
        filter_progress.empty()
        filter_status.empty()
                
    except Exception as e:
        st.error("Error creating filters: {}".format(str(e)))
        st.info("Using original dataset without filters.")
        filtered_data = data
        filter_summary = {'error': str(e), 'filtered_records': len(data), 'retention_rate': 1.0}
    
    # Render main dashboard with comprehensive error handling
    try:
        if filtered_data is not None and len(filtered_data) > 0:
            # Show dashboard loading progress
            dashboard_progress = st.progress(0)
            dashboard_status = st.empty()
            
            dashboard_status.text("📊 Preparing dashboard...")
            dashboard_progress.progress(20)
            
            # Try to add data quality check
            try:
                from analysis.data_quality import validate_dashboard_data
                
                with st.expander("📊 Data Quality Report", expanded=False):
                    validator, quality_results = validate_dashboard_data(filtered_data)
                    validator.generate_quality_report_display(quality_results)
            except ImportError:
                st.info("💡 Data quality analysis module not available")
            except Exception as e:
                st.warning("Data quality analysis failed: {}".format(str(e)))
            
            dashboard_progress.progress(50)
            dashboard_status.text("🎨 Rendering dashboard components...")
            
            # Render main dashboard with loading feedback
            with st.spinner("Generating visualizations..."):
                try:
                    create_dashboard_layout(filtered_data, filter_summary)
                except Exception as e:
                    st.error("Main dashboard failed: {}. Switching to fallback mode.".format(str(e)))
                    create_fallback_dashboard(filtered_data)
            
            dashboard_progress.progress(90)
            dashboard_status.text("✅ Dashboard ready!")
            
            # Add performance footer
            st.markdown("---")
            st.subheader("📊 Dashboard Performance")
            
            perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4)
            
            with perf_col1:
                st.metric(
                    "Dataset Size",
                    "{:,}".format(len(filtered_data)),
                    help="Number of records currently displayed"
                )
            
            with perf_col2:
                try:
                    memory_usage = filtered_data.memory_usage(deep=True).sum() / 1024 / 1024
                    st.metric(
                        "Memory Usage",
                        "{:.1f} MB".format(memory_usage),
                        help="Current memory consumption"
                    )
                except:
                    st.metric("Memory Usage", "N/A", help="Could not calculate memory usage")
            
            with perf_col3:
                columns_count = len(filtered_data.columns)
                st.metric(
                    "Data Columns",
                    columns_count,
                    help="Number of data columns available"
                )
            
            with perf_col4:
                last_updated = pd.Timestamp.now().strftime("%H:%M:%S")
                st.metric(
                    "Last Updated",
                    last_updated,
                    help="Time of last dashboard refresh"
                )
            
            dashboard_progress.progress(100)
            
            # Clear progress indicators
            import time
            time.sleep(0.5)
            dashboard_progress.empty()
            dashboard_status.empty()
            
        else:
            # Enhanced empty data handling
            st.error("🚫 No data available after filtering")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.info("""
                **Possible solutions:**
                - Reset all filters using the sidebar
                - Relax some filter criteria
                - Check if data files are properly loaded
                """)
            
            with col2:
                if st.button("🔄 Reset All Filters", key="main_reset_button"):
                    # Clear all session state
                    for key in list(st.session_state.keys()):
                        if 'filter' in key.lower() or 'selected' in key.lower():
                            del st.session_state[key]
                    st.rerun()
            
            # Show filter summary if available
            if filter_summary and 'filter_steps' in filter_summary:
                with st.expander("🔍 Filter Application Steps", expanded=True):
                    for step in filter_summary['filter_steps']:
                        st.text("• {}".format(step))
            
    except Exception as e:
        st.error("Critical error rendering dashboard: {}".format(str(e)))
        
        # Ultimate fallback
        with st.expander("🔧 Technical Details", expanded=False):
            st.code("Error: {}".format(str(e)))
            st.code("Error type: {}".format(type(e).__name__))
        
        st.info("🔄 Attempting fallback display...")
        create_fallback_dashboard(filtered_data if 'filtered_data' in locals() else data)

if __name__ == "__main__":
    main()