# -*- coding: utf-8 -*-
"""
Air Quality vs Middle-Class Income Dashboard

A Streamlit application for exploratory analysis of relationships between 
air quality indicators, respiratory hospitalization burden, and economic stress indicators.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import our custom modules
try:
    from data.real_data_processor import RealDataProcessor
    from ui.sidebar_filters import create_sidebar_filters
    from ui.dashboard_layout import create_dashboard_layout
except ImportError as e:
    st.error("Error importing modules: {}. Please ensure all dependencies are installed.".format(str(e)))
    st.stop()


def prepare_data_for_streamlit(df):
    """
    Prepare DataFrame for Streamlit display by fixing common conversion issues.
    
    Args:
        df: pandas DataFrame
        
    Returns:
        DataFrame safe for Streamlit display
    """
    if df is None or len(df) == 0:
        return df
    
    display_df = df.copy()
    
    # Fix datetime columns that cause PyArrow conversion issues
    for col in display_df.columns:
        if pd.api.types.is_datetime64_any_dtype(display_df[col]):
            # Convert datetime to string for display
            display_df[col] = display_df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
        elif display_df[col].dtype == 'object':
            # Handle mixed types in object columns
            try:
                # Try to convert timestamps in object columns
                if display_df[col].astype(str).str.contains('Timestamp').any():
                    display_df[col] = pd.to_datetime(display_df[col], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                pass
    
    return display_df


@st.cache_data(show_spinner=True, ttl=3600)  # Cache for 1 hour
def load_data():
    """Load and cache the real dataset with performance optimization."""
    try:
        with st.spinner("Loading and processing air quality data..."):
            processor = RealDataProcessor()
            merged_data = processor.create_comprehensive_dataset()
            
            # Optimize data types for better performance
            merged_data = optimize_data_types(merged_data)
            
        return merged_data, processor
    except Exception as e:
        st.error("Error loading data: {}".format(str(e)))
        return None, None


def optimize_data_types(df):
    """Optimize DataFrame data types for better performance."""
    optimized_df = df.copy()
    
    # Convert float64 to float32 where appropriate
    float_cols = optimized_df.select_dtypes(include=['float64']).columns
    for col in float_cols:
        if optimized_df[col].max() < 1e6:  # Safe range for float32
            optimized_df[col] = optimized_df[col].astype('float32')
    
    # Convert int64 to smaller int types where appropriate
    int_cols = optimized_df.select_dtypes(include=['int64']).columns
    for col in int_cols:
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
    
    return optimized_df


def main():
    """Main application entry point"""
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
    
    # Add custom CSS for better UI and production optimization
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
    /* Production optimizations */
    .stSpinner {
        text-align: center;
    }
    .stProgress .st-bo {
        background-color: #ff6b6b;
    }
    /* Hide Streamlit branding in production */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
    
    # Add progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Load data with progress updates
    status_text.text("Initializing data loader...")
    progress_bar.progress(10)
    
    data, processor = load_data()
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
    
    # Create sidebar filters and get filtered data
    try:
        with st.spinner("Applying filters..."):
            filtered_data, filter_summary = create_sidebar_filters(data)
            
        # Show filter performance info
        if filter_summary:
            retention_rate = filter_summary.get('retention_rate', 1.0)
            if retention_rate < 0.1:  # Less than 10% data retained
                st.warning("⚠️ Current filters are very restrictive ({:.1%} data retained). Consider relaxing some filters for better analysis.".format(retention_rate))
            elif retention_rate < 0.5:  # Less than 50% data retained
                st.info("ℹ️ Filters have significantly reduced the dataset ({:.1%} retained). Results may be limited.".format(retention_rate))
                
    except Exception as e:
        st.error("Error creating filters: {}".format(str(e)))
        filtered_data = data
        filter_summary = None
    
    # Render main dashboard with performance monitoring
    try:
        if filtered_data is not None and len(filtered_data) > 0:
            # Add data quality check
            from analysis.data_quality import validate_dashboard_data
            
            with st.expander("📊 Data Quality Report", expanded=False):
                validator, quality_results = validate_dashboard_data(filtered_data)
                validator.generate_quality_report_display(quality_results)
            
            # Render main dashboard
            create_dashboard_layout(filtered_data, filter_summary)
            
            # Add performance footer
            st.markdown("---")
            perf_col1, perf_col2, perf_col3 = st.columns(3)
            
            with perf_col1:
                st.caption("📈 Dataset: {:,} records".format(len(filtered_data)))
            
            with perf_col2:
                memory_usage = filtered_data.memory_usage(deep=True).sum() / 1024 / 1024
                st.caption("💾 Memory: {:.1f} MB".format(memory_usage))
            
            with perf_col3:
                st.caption("🔄 Last updated: {}".format(
                    pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                ))
        else:
            st.error("No data available after filtering. Please adjust your filter settings.")
            
    except Exception as e:
        st.error("Error rendering dashboard: {}".format(str(e)))
        st.info("Falling back to basic data display...")
        
        # Fallback: basic data display
        st.title("🌬️ Air Quality vs Middle-Class Income Dashboard")
        st.warning("""
        **DISCLAIMER**: This dashboard is for reference and exploratory analysis only. 
        It makes no medical claims or predictions.
        """)
        
        if filtered_data is not None and len(filtered_data) > 0:
            st.subheader("Data Overview")
            st.write("Dataset shape: {} rows, {} columns".format(*filtered_data.shape))
            
            # Fix timestamp conversion issue for display
            display_data = prepare_data_for_streamlit(filtered_data.head())
            st.dataframe(display_data)
            
            # Basic statistics
            st.subheader("Basic Statistics")
            st.write(filtered_data.describe())
        else:
            st.error("No data available after filtering.")


if __name__ == "__main__":
    main()