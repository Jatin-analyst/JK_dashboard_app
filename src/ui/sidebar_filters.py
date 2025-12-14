"""
Sidebar filter controls for the Air Quality vs Income Dashboard.

This module creates comprehensive Streamlit sidebar widgets for filtering
the dashboard data across multiple dimensions.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from filters.filter_manager import FilterManager


class SidebarFilters:
    """
    Creates and manages sidebar filter controls for the dashboard.
    """
    
    def __init__(self):
        """Initialize the sidebar filters."""
        self.filter_manager = FilterManager()
        self.available_values = {}
    
    def initialize_filters(self, data):
        """
        Initialize filters with data and get available values.
        
        Args:
            data: DataFrame to initialize filters with
        """
        self.filter_manager.set_data(data)
        self.available_values = self.filter_manager.get_available_filter_values()
        return self
    
    def create_location_filters(self):
        """Create location-based filter controls."""
        st.sidebar.subheader("📍 Geographic Filters")
        
        # Location multi-select
        locations = self.available_values.get('locations', [])
        if locations:
            selected_locations = st.sidebar.multiselect(
                "Select Locations",
                options=locations,
                default=locations,  # All selected by default
                help="Choose specific cities or regions to analyze"
            )
        else:
            selected_locations = []
            st.sidebar.info("No location data available")
        
        return selected_locations
    
    def create_demographic_filters(self):
        """Create demographic filter controls."""
        st.sidebar.subheader("👥 Demographic Filters")
        
        # Age group multi-select
        age_groups = self.available_values.get('age_groups', [])
        if age_groups:
            selected_age_groups = st.sidebar.multiselect(
                "Age Groups",
                options=age_groups,
                default=age_groups,
                help="Filter by age demographics"
            )
        else:
            selected_age_groups = []
        
        # Gender multi-select
        genders = self.available_values.get('genders', [])
        if genders:
            selected_genders = st.sidebar.multiselect(
                "Gender",
                options=genders,
                default=genders,
                help="Filter by gender demographics"
            )
        else:
            selected_genders = []
        
        return {
            'age_groups': selected_age_groups,
            'genders': selected_genders
        }
    
    def create_environmental_filters(self):
        """Create environmental and pollution filter controls."""
        st.sidebar.subheader("🌍 Environmental Filters")
        
        # Season multi-select
        seasons = self.available_values.get('seasons', [])
        if seasons:
            selected_seasons = st.sidebar.multiselect(
                "Seasons",
                options=seasons,
                default=seasons,
                help="Filter by seasonal patterns"
            )
        else:
            selected_seasons = []
        
        # AQI range slider
        numeric_ranges = self.available_values.get('numeric_ranges', {})
        aqi_range = numeric_ranges.get('aqi', {'min': 0, 'max': 500})
        
        st.sidebar.write("**Air Quality Index (AQI)**")
        aqi_min, aqi_max = st.sidebar.slider(
            "AQI Range",
            min_value=int(aqi_range['min']),
            max_value=int(aqi_range['max']),
            value=(int(aqi_range['min']), int(aqi_range['max'])),
            help="Filter by Air Quality Index levels"
        )
        
        # PM2.5 range slider
        pm25_range = numeric_ranges.get('pm25', {'min': 0, 'max': 200})
        
        st.sidebar.write("**PM2.5 Levels (μg/m³)**")
        pm25_min, pm25_max = st.sidebar.slider(
            "PM2.5 Range",
            min_value=float(pm25_range['min']),
            max_value=float(pm25_range['max']),
            value=(float(pm25_range['min']), float(pm25_range['max'])),
            help="Filter by PM2.5 particulate matter levels"
        )
        
        return {
            'seasons': selected_seasons,
            'aqi_min': aqi_min,
            'aqi_max': aqi_max,
            'pm25_min': pm25_min,
            'pm25_max': pm25_max
        }
    
    def create_temporal_filters(self):
        """Create temporal filter controls."""
        st.sidebar.subheader("📅 Temporal Filters")
        
        # Date range
        date_range = self.available_values.get('date_range', {})
        if date_range:
            min_date = date_range['min'].date() if hasattr(date_range['min'], 'date') else date_range['min']
            max_date = date_range['max'].date() if hasattr(date_range['max'], 'date') else date_range['max']
            
            start_date = st.sidebar.date_input(
                "Start Date",
                value=min_date,
                min_value=min_date,
                max_value=max_date,
                help="Select the start date for analysis"
            )
            
            end_date = st.sidebar.date_input(
                "End Date",
                value=max_date,
                min_value=min_date,
                max_value=max_date,
                help="Select the end date for analysis"
            )
            
            # Validate date range
            if start_date > end_date:
                st.sidebar.error("Start date must be before end date")
                start_date = min_date
                end_date = max_date
        else:
            start_date = None
            end_date = None
            st.sidebar.info("No date data available")
        
        return {
            'start_date': start_date,
            'end_date': end_date
        }
    
    def create_threshold_filters(self):
        """Create threshold-based filter controls."""
        st.sidebar.subheader("📊 Threshold Filters")
        
        numeric_ranges = self.available_values.get('numeric_ranges', {})
        
        # Respiratory cases threshold
        resp_range = numeric_ranges.get('respiratory_cases', {'min': 0, 'max': 100})
        
        st.sidebar.write("**Respiratory Cases**")
        resp_min, resp_max = st.sidebar.slider(
            "Respiratory Cases Range",
            min_value=int(resp_range['min']),
            max_value=int(resp_range['max']),
            value=(int(resp_range['min']), int(resp_range['max'])),
            help="Filter by number of respiratory cases"
        )
        
        # Income stress threshold (if available)
        income_stress_enabled = st.sidebar.checkbox(
            "Enable Income Stress Filtering",
            value=False,
            help="Filter by calculated income stress index"
        )
        
        income_stress_min = None
        income_stress_max = None
        
        if income_stress_enabled:
            st.sidebar.write("**Income Stress Index**")
            income_stress_min = st.sidebar.number_input(
                "Minimum Income Stress",
                min_value=0.0,
                value=500.0,
                help="Minimum income stress index value"
            )
            income_stress_max = st.sidebar.number_input(
                "Maximum Income Stress",
                min_value=income_stress_min,
                value=5000.0,
                help="Maximum income stress index value"
            )
        
        return {
            'respiratory_cases_min': resp_min,
            'respiratory_cases_max': resp_max,
            'income_stress_min': income_stress_min,
            'income_stress_max': income_stress_max
        }
    
    def create_statistical_filters(self):
        """Create statistical and data quality filter controls."""
        st.sidebar.subheader("📈 Statistical Filters")
        
        # Sample size requirement
        min_sample_size = st.sidebar.number_input(
            "Minimum Sample Size",
            min_value=1,
            max_value=1000,
            value=10,
            help="Minimum number of records required for analysis"
        )
        
        # Data completeness requirement
        min_completeness = st.sidebar.slider(
            "Minimum Data Completeness",
            min_value=0.0,
            max_value=1.0,
            value=0.8,
            step=0.05,
            format="%.0%%",
            help="Minimum percentage of complete data required"
        )
        
        # Outlier exclusion
        exclude_outliers = st.sidebar.checkbox(
            "Exclude Statistical Outliers",
            value=False,
            help="Remove statistical outliers using IQR method"
        )
        
        return {
            'sample_size_min': min_sample_size,
            'data_completeness_min': min_completeness,
            'exclude_outliers': exclude_outliers
        }
    
    def create_filter_summary(self):
        """Create filter summary and control section."""
        st.sidebar.subheader("🔧 Filter Controls")
        
        # Reset filters button
        if st.sidebar.button("Reset All Filters", help="Clear all filters and return to original data"):
            # Clear session state filter values
            filter_keys = [
                'selected_locations', 'selected_demographics', 'selected_environmental',
                'selected_temporal', 'selected_thresholds', 'selected_statistical'
            ]
            for key in filter_keys:
                if key in st.session_state:
                    del st.session_state[key]
            st.experimental_rerun()
        
        # Export filtered data button
        if st.sidebar.button("Export Filtered Data", help="Download current filtered dataset"):
            # This would trigger a download in a real implementation
            st.sidebar.success("Export functionality would be implemented here")
    
    def apply_all_filters(self, data, location_filters, demographic_filters, 
                         environmental_filters, temporal_filters, threshold_filters, 
                         statistical_filters):
        """
        Apply all selected filters to the data.
        
        Args:
            data: Original DataFrame
            location_filters: Location filter selections
            demographic_filters: Demographic filter selections
            environmental_filters: Environmental filter selections
            temporal_filters: Temporal filter selections
            threshold_filters: Threshold filter selections
            statistical_filters: Statistical filter selections
            
        Returns:
            Filtered DataFrame and filter summary
        """
        # Initialize filter manager with data
        self.filter_manager.set_data(data)
        
        # Apply filters in sequence
        if location_filters:
            self.filter_manager.apply_location_filter(location_filters)
        
        if demographic_filters['age_groups'] or demographic_filters['genders']:
            self.filter_manager.apply_demographic_filter(
                age_groups=demographic_filters['age_groups'] if demographic_filters['age_groups'] else None,
                genders=demographic_filters['genders'] if demographic_filters['genders'] else None
            )
        
        if any([environmental_filters['seasons'], 
                environmental_filters['aqi_min'] != environmental_filters['aqi_max'],
                environmental_filters['pm25_min'] != environmental_filters['pm25_max']]):
            self.filter_manager.apply_environmental_filter(
                seasons=environmental_filters['seasons'] if environmental_filters['seasons'] else None,
                aqi_min=environmental_filters['aqi_min'],
                aqi_max=environmental_filters['aqi_max'],
                pm25_min=environmental_filters['pm25_min'],
                pm25_max=environmental_filters['pm25_max']
            )
        
        if temporal_filters['start_date'] or temporal_filters['end_date']:
            self.filter_manager.apply_temporal_filter(
                start_date=temporal_filters['start_date'],
                end_date=temporal_filters['end_date']
            )
        
        if any([threshold_filters['respiratory_cases_min'] != threshold_filters['respiratory_cases_max'],
                threshold_filters['income_stress_min'] is not None]):
            self.filter_manager.apply_threshold_filter(
                respiratory_cases_min=threshold_filters['respiratory_cases_min'],
                respiratory_cases_max=threshold_filters['respiratory_cases_max'],
                income_stress_min=threshold_filters['income_stress_min'],
                income_stress_max=threshold_filters['income_stress_max']
            )
        
        # Always apply statistical filters (they have built-in checks for meaningful values)
        self.filter_manager.apply_statistical_filter(
            sample_size_min=statistical_filters['sample_size_min'],
            data_completeness_min=statistical_filters['data_completeness_min'],
            exclude_outliers=statistical_filters['exclude_outliers']
        )
        
        # Get filtered data and summary
        filtered_data = self.filter_manager.get_filtered_dataset()
        filter_summary = self.filter_manager.get_filter_summary()
        
        return filtered_data, filter_summary
    
    def render_complete_sidebar(self, data):
        """
        Render the complete sidebar with all filter controls.
        
        Args:
            data: DataFrame to create filters for
            
        Returns:
            Tuple of (filtered_data, filter_summary)
        """
        # Initialize filters with data
        self.initialize_filters(data)
        
        # Create filter sections
        st.sidebar.title("🎛️ Dashboard Filters")
        st.sidebar.markdown("---")
        
        # Location filters
        location_filters = self.create_location_filters()
        st.sidebar.markdown("---")
        
        # Demographic filters
        demographic_filters = self.create_demographic_filters()
        st.sidebar.markdown("---")
        
        # Environmental filters
        environmental_filters = self.create_environmental_filters()
        st.sidebar.markdown("---")
        
        # Temporal filters
        temporal_filters = self.create_temporal_filters()
        st.sidebar.markdown("---")
        
        # Threshold filters
        threshold_filters = self.create_threshold_filters()
        st.sidebar.markdown("---")
        
        # Statistical filters
        statistical_filters = self.create_statistical_filters()
        st.sidebar.markdown("---")
        
        # Filter controls
        self.create_filter_summary()
        
        # Apply all filters
        filtered_data, filter_summary = self.apply_all_filters(
            data, location_filters, demographic_filters, environmental_filters,
            temporal_filters, threshold_filters, statistical_filters
        )
        
        # Display filter summary
        st.sidebar.markdown("---")
        st.sidebar.subheader("📋 Filter Summary")
        st.sidebar.metric(
            "Records Shown", 
            filter_summary['filtered_records'],
            delta=filter_summary['records_removed'] * -1
        )
        st.sidebar.metric(
            "Retention Rate",
            "{:.1%}".format(filter_summary['retention_rate'])
        )
        st.sidebar.metric(
            "Active Filters",
            filter_summary['active_filters']
        )
        
        return filtered_data, filter_summary


def create_sidebar_filters(data):
    """
    Convenience function to create sidebar filters.
    
    Args:
        data: DataFrame to create filters for
        
    Returns:
        Tuple of (filtered_data, filter_summary)
    """
    sidebar_filters = SidebarFilters()
    return sidebar_filters.render_complete_sidebar(data)


if __name__ == "__main__":
    # This would be used in the main Streamlit app
    print("Sidebar filters module loaded successfully!")
    print("Use create_sidebar_filters(data) in your Streamlit app to add comprehensive filtering.")