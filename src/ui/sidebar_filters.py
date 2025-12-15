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
        
        # Location multi-select with enhanced help
        locations = self.available_values.get('locations', [])
        if locations:
            st.sidebar.caption("{} locations available".format(len(locations)))
            selected_locations = st.sidebar.multiselect(
                "Select Locations",
                options=locations,
                default=locations,  # All selected by default
                help="""
                Choose specific cities or regions to analyze.
                
                Available locations: {}
                Tip: Select fewer locations for focused analysis
                Use 'Select All' to include all locations
                """.format(len(locations))
            )
            
            # Show selection summary
            if len(selected_locations) != len(locations):
                st.sidebar.caption("Selected: {}/{} locations".format(len(selected_locations), len(locations)))
        else:
            selected_locations = []
            st.sidebar.warning("⚠️ No location data available")
            st.sidebar.caption("Check if data files are properly loaded")
        
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
        
        # Season multi-select with enhanced help
        seasons = self.available_values.get('seasons', [])
        if seasons:
            st.sidebar.caption("{} seasons available".format(len(seasons)))
            selected_seasons = st.sidebar.multiselect(
                "Seasons",
                options=seasons,
                default=seasons,
                help="""
                Filter by seasonal patterns to analyze weather-related trends.
                
                🌸 Spring: March-May
                ☀️ Summer: June-August  
                🍂 Fall: September-November
                ❄️ Winter: December-February
                """
            )
        else:
            selected_seasons = []
            st.sidebar.info("ℹ️ No seasonal data available")
        
        # AQI range slider with quality indicators
        numeric_ranges = self.available_values.get('numeric_ranges', {})
        aqi_range = numeric_ranges.get('aqi', {'min': 0, 'max': 500})
        
        st.sidebar.write("**🌫️ Air Quality Index (AQI)**")
        aqi_min, aqi_max = st.sidebar.slider(
            "AQI Range",
            min_value=int(aqi_range['min']),
            max_value=int(aqi_range['max']),
            value=(int(aqi_range['min']), int(aqi_range['max'])),
            help="""
            Air Quality Index scale:
            
            🟢 Good: 0-50
            🟡 Moderate: 51-100
            🟠 Unhealthy for Sensitive: 101-150
            🔴 Unhealthy: 151-200
            🟣 Very Unhealthy: 201-300
            🟤 Hazardous: 301+
            """
        )
        
        # Show AQI quality indicator
        if aqi_min <= 50 and aqi_max <= 50:
            st.sidebar.success("🟢 Good air quality range")
        elif aqi_min <= 100 and aqi_max <= 100:
            st.sidebar.info("🟡 Moderate air quality range")
        elif aqi_max > 200:
            st.sidebar.error("🔴 Unhealthy air quality range")
        else:
            st.sidebar.warning("🟠 Sensitive groups affected")
        
        # PM2.5 range slider with health context
        pm25_range = numeric_ranges.get('pm25', {'min': 0, 'max': 200})
        
        st.sidebar.write("**🔬 PM2.5 Levels (μg/m³)**")
        pm25_min, pm25_max = st.sidebar.slider(
            "PM2.5 Range",
            min_value=float(pm25_range['min']),
            max_value=float(pm25_range['max']),
            value=(float(pm25_range['min']), float(pm25_range['max'])),
            help="""
            PM2.5 (fine particulate matter) guidelines:
            
            🟢 WHO Guideline: ≤15 μg/m³ (annual)
            🟡 Moderate: 15-35 μg/m³
            🟠 High: 35-75 μg/m³
            🔴 Very High: >75 μg/m³
            
            Lower values indicate cleaner air.
            """
        )
        
        # Show PM2.5 health indicator
        if pm25_max <= 15:
            st.sidebar.success("🟢 WHO guideline compliant")
        elif pm25_max <= 35:
            st.sidebar.info("🟡 Moderate PM2.5 levels")
        elif pm25_max <= 75:
            st.sidebar.warning("🟠 High PM2.5 levels")
        else:
            st.sidebar.error("🔴 Very high PM2.5 levels")
        
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
        
        # Date range with improved error handling
        date_range = self.available_values.get('date_range', {})
        if date_range and 'min' in date_range and 'max' in date_range:
            try:
                min_date = date_range['min']
                max_date = date_range['max']
                
                # Convert to date objects if they're datetime
                if hasattr(min_date, 'date'):
                    min_date = min_date.date()
                elif isinstance(min_date, str):
                    min_date = pd.to_datetime(min_date).date()
                
                if hasattr(max_date, 'date'):
                    max_date = max_date.date()
                elif isinstance(max_date, str):
                    max_date = pd.to_datetime(max_date).date()
            except Exception as e:
                min_date = None
                max_date = None
                st.sidebar.warning("Date range processing error: {}".format(str(e)))
        else:
            min_date = None
            max_date = None
            
        if min_date and max_date:
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
        
        # Initialize session state for statistical filters
        if 'statistical_filters_enabled' not in st.session_state:
            st.session_state.statistical_filters_enabled = False
        
        # Enable/disable statistical filtering
        enable_statistical = st.sidebar.checkbox(
            "Enable Advanced Statistical Filtering",
            value=st.session_state.statistical_filters_enabled,
            key="enable_statistical_filters",
            help="Turn on advanced statistical filtering options"
        )
        
        if enable_statistical != st.session_state.statistical_filters_enabled:
            st.session_state.statistical_filters_enabled = enable_statistical
        
        if enable_statistical:
            # Sample size requirement with validation
            current_data_size = len(self.available_values.get('locations', [])) * 100  # Rough estimate
            max_reasonable_sample = min(1000, current_data_size)
            
            min_sample_size = st.sidebar.number_input(
                "Minimum Sample Size",
                min_value=1,
                max_value=max_reasonable_sample,
                value=min(st.session_state.get('min_sample_size', 10), max_reasonable_sample),
                key="statistical_sample_size",
                help="Minimum number of records required for analysis"
            )
            
            # Real-time validation for sample size
            if hasattr(self, 'filter_manager') and self.filter_manager.filtered_data is not None:
                current_size = len(self.filter_manager.filtered_data)
                if current_size < min_sample_size:
                    st.sidebar.error("Sample size ({}) > available data ({:,})".format(min_sample_size, current_size))
                elif current_size < min_sample_size * 2:
                    st.sidebar.warning("Sample size close to data limit ({:,} available)".format(current_size))
                else:
                    st.sidebar.success("Sample size OK ({:,} available)".format(current_size))
            
            # Data completeness requirement with preview
            min_completeness = st.sidebar.slider(
                "Minimum Data Completeness",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.get('min_completeness', 0.8),
                step=0.05,
                format="%.0%%",
                key="statistical_completeness",
                help="Minimum percentage of complete data required"
            )
            
            # Show completeness impact
            if min_completeness > 0.9:
                st.sidebar.warning("⚠️ Very high completeness requirement may exclude most data")
            elif min_completeness > 0.7:
                st.sidebar.info("ℹ️ Moderate completeness requirement")
            
            # Outlier exclusion with explanation
            exclude_outliers = st.sidebar.checkbox(
                "Exclude Statistical Outliers",
                value=st.session_state.get('exclude_outliers', False),
                key="statistical_outliers",
                help="Remove statistical outliers using IQR method (removes ~5% of extreme values)"
            )
            
            if exclude_outliers:
                st.sidebar.caption("📊 Outliers removed using Interquartile Range (IQR) method")
            
            # Store values in session state
            st.session_state.min_sample_size = min_sample_size
            st.session_state.min_completeness = min_completeness
            st.session_state.exclude_outliers = exclude_outliers
            
            # Validate filter combination
            if hasattr(self, 'filter_manager'):
                validation = self.filter_manager.validate_filter_combination(
                    sample_size_min=min_sample_size,
                    data_completeness_min=min_completeness,
                    exclude_outliers=exclude_outliers
                )
                
                if validation['warnings']:
                    for warning in validation['warnings']:
                        st.sidebar.warning("{}".format(warning))
            
            return {
                'sample_size_min': min_sample_size,
                'data_completeness_min': min_completeness,
                'exclude_outliers': exclude_outliers
            }
        else:
            # Return default values when disabled
            return {
                'sample_size_min': 1,
                'data_completeness_min': 0.0,
                'exclude_outliers': False
            }
    
    def create_filter_summary(self):
        """Create filter summary and control section."""
        st.sidebar.subheader("🔧 Filter Controls")
        
        # Reset filters button with improved functionality
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            if st.button("🔄 Reset All", key="reset_all_filters", help="Clear all filters and return to original data"):
                # Clear all filter-related session state
                filter_keys = [
                    'selected_locations', 'selected_demographics', 'selected_environmental',
                    'selected_temporal', 'selected_thresholds', 'selected_statistical',
                    'statistical_filters_enabled', 'min_sample_size', 'min_completeness',
                    'exclude_outliers', 'selected_pollutant', 'last_filter_hash'
                ]
                for key in filter_keys:
                    if key in st.session_state:
                        del st.session_state[key]
                
                # Reset to default values
                st.session_state.selected_pollutant = 'AQI'
                st.session_state.statistical_filters_enabled = False
                
                st.sidebar.success("✅ Filters reset!")
                st.rerun()
        
        with col2:
            if st.button("📊 Apply", key="apply_filters", help="Apply current filter settings"):
                st.rerun()
        
        # Export filtered data button
        if st.sidebar.button("📥 Export Data", key="export_filtered_data", help="Download current filtered dataset"):
            # This would trigger a download in a real implementation
            st.sidebar.info("📋 Export functionality available in full version")
    
    def apply_all_filters(self, data, location_filters, demographic_filters, 
                         environmental_filters, temporal_filters, threshold_filters, 
                         statistical_filters):
        """
        Apply all selected filters to the data with improved error handling and feedback.
        
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
        try:
            # Initialize filter manager with data
            self.filter_manager.set_data(data)
            original_size = len(data)
            
            # Track filter application progress
            filter_steps = []
            
            # Apply location filters
            if location_filters:
                before_size = len(self.filter_manager.get_filtered_dataset())
                self.filter_manager.apply_location_filter(location_filters)
                after_size = len(self.filter_manager.get_filtered_dataset())
                filter_steps.append("Location: {} → {} records".format(before_size, after_size))
            
            # Apply demographic filters
            if demographic_filters['age_groups'] or demographic_filters['genders']:
                before_size = len(self.filter_manager.get_filtered_dataset())
                self.filter_manager.apply_demographic_filter(
                    age_groups=demographic_filters['age_groups'] if demographic_filters['age_groups'] else None,
                    genders=demographic_filters['genders'] if demographic_filters['genders'] else None
                )
                after_size = len(self.filter_manager.get_filtered_dataset())
                filter_steps.append("Demographics: {} → {} records".format(before_size, after_size))
            
            # Apply environmental filters
            env_filters_active = any([
                environmental_filters['seasons'], 
                environmental_filters['aqi_min'] != environmental_filters['aqi_max'],
                environmental_filters['pm25_min'] != environmental_filters['pm25_max']
            ])
            
            if env_filters_active:
                before_size = len(self.filter_manager.get_filtered_dataset())
                self.filter_manager.apply_environmental_filter(
                    seasons=environmental_filters['seasons'] if environmental_filters['seasons'] else None,
                    aqi_min=environmental_filters['aqi_min'],
                    aqi_max=environmental_filters['aqi_max'],
                    pm25_min=environmental_filters['pm25_min'],
                    pm25_max=environmental_filters['pm25_max']
                )
                after_size = len(self.filter_manager.get_filtered_dataset())
                filter_steps.append("Environmental: {} → {} records".format(before_size, after_size))
            
            # Apply temporal filters
            if temporal_filters['start_date'] or temporal_filters['end_date']:
                before_size = len(self.filter_manager.get_filtered_dataset())
                self.filter_manager.apply_temporal_filter(
                    start_date=temporal_filters['start_date'],
                    end_date=temporal_filters['end_date']
                )
                after_size = len(self.filter_manager.get_filtered_dataset())
                filter_steps.append("Temporal: {} → {} records".format(before_size, after_size))
            
            # Apply threshold filters
            threshold_filters_active = any([
                threshold_filters['respiratory_cases_min'] != threshold_filters['respiratory_cases_max'],
                threshold_filters['income_stress_min'] is not None
            ])
            
            if threshold_filters_active:
                before_size = len(self.filter_manager.get_filtered_dataset())
                self.filter_manager.apply_threshold_filter(
                    respiratory_cases_min=threshold_filters['respiratory_cases_min'],
                    respiratory_cases_max=threshold_filters['respiratory_cases_max'],
                    income_stress_min=threshold_filters['income_stress_min'],
                    income_stress_max=threshold_filters['income_stress_max']
                )
                after_size = len(self.filter_manager.get_filtered_dataset())
                filter_steps.append("Thresholds: {} → {} records".format(before_size, after_size))
            
            # Apply statistical filters if enabled
            statistical_active = (
                statistical_filters['sample_size_min'] > 1 or 
                statistical_filters['data_completeness_min'] > 0.0 or 
                statistical_filters['exclude_outliers']
            )
            
            if statistical_active:
                before_size = len(self.filter_manager.get_filtered_dataset())
                
                # Validate before applying
                validation = self.filter_manager.validate_filter_combination(**statistical_filters)
                
                if validation['is_valid'] or before_size > 0:
                    self.filter_manager.apply_statistical_filter(
                        sample_size_min=statistical_filters['sample_size_min'],
                        data_completeness_min=statistical_filters['data_completeness_min'],
                        exclude_outliers=statistical_filters['exclude_outliers']
                    )
                    after_size = len(self.filter_manager.get_filtered_dataset())
                    filter_steps.append("Statistical: {} → {} records".format(before_size, after_size))
                    
                    # Add warnings to filter steps if any
                    if validation['warnings']:
                        for warning in validation['warnings']:
                            filter_steps.append("{}".format(warning))
                else:
                    filter_steps.append("Statistical: Skipped (would result in empty dataset)")
            
            # Get filtered data and summary
            filtered_data = self.filter_manager.get_filtered_dataset()
            filter_summary = self.filter_manager.get_filter_summary()
            
            # Add filter steps to summary
            filter_summary['filter_steps'] = filter_steps
            
            # Check for potential issues
            final_size = len(filtered_data)
            if final_size == 0:
                st.sidebar.error("⚠️ All data filtered out! Please relax some filters.")
            elif final_size < 10:
                st.sidebar.warning("Very small dataset ({} records). Results may be unreliable.".format(final_size))
            elif final_size / original_size < 0.1:
                st.sidebar.warning("Filters removed {:.1f}% of data.".format(((original_size - final_size) / original_size * 100)))
            
            return filtered_data, filter_summary
            
        except Exception as e:
            st.sidebar.error("Error applying filters: {}".format(str(e)))
            return data, {
                'error': str(e), 
                'original_records': len(data), 
                'filtered_records': len(data),
                'records_removed': 0,
                'retention_rate': 1.0,
                'active_filters': 0,
                'filter_details': {}
            }
    
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
        
        # Display enhanced filter summary
        st.sidebar.markdown("---")
        st.sidebar.subheader("📋 Filter Summary")
        
        # Main metrics
        col1, col2 = st.sidebar.columns(2)
        with col1:
            records_removed = filter_summary.get('records_removed', 0)
            st.metric(
                "Records", 
                "{:,}".format(filter_summary['filtered_records']),
                delta="-{:,}".format(records_removed) if records_removed > 0 else None
            )
        with col2:
            st.metric(
                "Retention",
                "{:.1%}".format(filter_summary['retention_rate']),
                delta="{} filters".format(filter_summary['active_filters'])
            )
        
        # Show filter steps if available
        if 'filter_steps' in filter_summary and filter_summary['filter_steps']:
            with st.sidebar.expander("🔍 Filter Details", expanded=False):
                for step in filter_summary['filter_steps']:
                    st.caption("• {}".format(step))
        
        # Data quality indicator
        retention_rate = filter_summary['retention_rate']
        if retention_rate >= 0.8:
            st.sidebar.success("🟢 Good data retention")
        elif retention_rate >= 0.5:
            st.sidebar.warning("🟡 Moderate data retention")
        elif retention_rate >= 0.1:
            st.sidebar.warning("🟠 Low data retention")
        else:
            st.sidebar.error("🔴 Very low data retention")
        
        return filtered_data, filter_summary


def create_sidebar_filters(data):
    """
    Convenience function to create sidebar filters with proper state management.
    
    Args:
        data: DataFrame to create filters for
        
    Returns:
        Tuple of (filtered_data, filter_summary)
    """
    # Initialize session state for filters if not exists
    if 'filter_state' not in st.session_state:
        st.session_state.filter_state = {}
    
    sidebar_filters = SidebarFilters()
    filtered_data, filter_summary = sidebar_filters.render_complete_sidebar(data)
    
    # Update the filter hash to trigger re-renders when filters change
    current_hash = hash(str(filtered_data.shape) + str(filter_summary))
    if st.session_state.get('last_filter_hash') != current_hash:
        st.session_state.last_filter_hash = current_hash
    
    return filtered_data, filter_summary


if __name__ == "__main__":
    # This would be used in the main Streamlit app
    print("Sidebar filters module loaded successfully!")
    print("Use create_sidebar_filters(data) in your Streamlit app to add comprehensive filtering.")