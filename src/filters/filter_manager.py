"""
Filter management module for the Air Quality vs Income Dashboard.

This module provides comprehensive filtering capabilities for the dashboard,
including geographic, demographic, environmental, temporal, and statistical filters.
"""

import pandas as pd
import numpy as np
from datetime import datetime


class FilterManager:
    """
    Manages all filtering operations for the dashboard data.
    """
    
    def __init__(self):
        """Initialize the FilterManager."""
        self.current_filters = {}
        self.original_data = None
        self.filtered_data = None
    
    def set_data(self, data):
        """Set the original dataset for filtering."""
        self.original_data = data.copy()
        self.filtered_data = data.copy()
        return self
    
    def apply_location_filter(self, locations=None):
        """
        Apply location-based filtering.
        
        Args:
            locations: List of location names to include, or None for all
        """
        if locations is None or len(locations) == 0:
            return self.filtered_data
        
        self.filtered_data = self.filtered_data[
            self.filtered_data['location'].isin(locations)
        ]
        self.current_filters['locations'] = locations
        return self.filtered_data
    
    def apply_demographic_filter(self, age_groups=None, genders=None):
        """
        Apply demographic filtering by age group and gender.
        
        Args:
            age_groups: List of age groups to include, or None for all
            genders: List of genders to include, or None for all
        """
        if age_groups is not None and len(age_groups) > 0:
            if 'age_group' in self.filtered_data.columns:
                self.filtered_data = self.filtered_data[
                    self.filtered_data['age_group'].isin(age_groups)
                ]
                self.current_filters['age_groups'] = age_groups
        
        if genders is not None and len(genders) > 0:
            if 'gender' in self.filtered_data.columns:
                self.filtered_data = self.filtered_data[
                    self.filtered_data['gender'].isin(genders)
                ]
                self.current_filters['genders'] = genders
        
        return self.filtered_data
    
    def apply_environmental_filter(self, seasons=None, aqi_min=None, aqi_max=None, 
                                 pm25_min=None, pm25_max=None):
        """
        Apply environmental filtering by season and pollution levels.
        
        Args:
            seasons: List of seasons to include, or None for all
            aqi_min: Minimum AQI value, or None for no minimum
            aqi_max: Maximum AQI value, or None for no maximum
            pm25_min: Minimum PM2.5 value, or None for no minimum
            pm25_max: Maximum PM2.5 value, or None for no maximum
        """
        if seasons is not None and len(seasons) > 0:
            if 'season' in self.filtered_data.columns:
                self.filtered_data = self.filtered_data[
                    self.filtered_data['season'].isin(seasons)
                ]
                self.current_filters['seasons'] = seasons
        
        if aqi_min is not None:
            if 'aqi' in self.filtered_data.columns:
                self.filtered_data = self.filtered_data[
                    self.filtered_data['aqi'] >= aqi_min
                ]
                self.current_filters['aqi_min'] = aqi_min
        
        if aqi_max is not None:
            if 'aqi' in self.filtered_data.columns:
                self.filtered_data = self.filtered_data[
                    self.filtered_data['aqi'] <= aqi_max
                ]
                self.current_filters['aqi_max'] = aqi_max
        
        if pm25_min is not None:
            if 'pm25' in self.filtered_data.columns:
                self.filtered_data = self.filtered_data[
                    self.filtered_data['pm25'] >= pm25_min
                ]
                self.current_filters['pm25_min'] = pm25_min
        
        if pm25_max is not None:
            if 'pm25' in self.filtered_data.columns:
                self.filtered_data = self.filtered_data[
                    self.filtered_data['pm25'] <= pm25_max
                ]
                self.current_filters['pm25_max'] = pm25_max
        
        return self.filtered_data
    
    def apply_temporal_filter(self, start_date=None, end_date=None):
        """
        Apply temporal filtering by date range.
        
        Args:
            start_date: Start date for filtering, or None for no start limit
            end_date: End date for filtering, or None for no end limit
        """
        if 'date' not in self.filtered_data.columns:
            return self.filtered_data
        
        # Ensure date column is datetime
        if not pd.api.types.is_datetime64_any_dtype(self.filtered_data['date']):
            self.filtered_data['date'] = pd.to_datetime(self.filtered_data['date'])
        
        if start_date is not None:
            if isinstance(start_date, str):
                start_date = pd.to_datetime(start_date)
            self.filtered_data = self.filtered_data[
                self.filtered_data['date'] >= start_date
            ]
            self.current_filters['start_date'] = start_date
        
        if end_date is not None:
            if isinstance(end_date, str):
                end_date = pd.to_datetime(end_date)
            self.filtered_data = self.filtered_data[
                self.filtered_data['date'] <= end_date
            ]
            self.current_filters['end_date'] = end_date
        
        return self.filtered_data
    
    def apply_threshold_filter(self, income_stress_min=None, income_stress_max=None,
                             respiratory_cases_min=None, respiratory_cases_max=None):
        """
        Apply threshold-based filtering for calculated metrics.
        
        Args:
            income_stress_min: Minimum income stress value
            income_stress_max: Maximum income stress value
            respiratory_cases_min: Minimum respiratory cases
            respiratory_cases_max: Maximum respiratory cases
        """
        if income_stress_min is not None:
            if 'income_stress_index' in self.filtered_data.columns:
                self.filtered_data = self.filtered_data[
                    self.filtered_data['income_stress_index'] >= income_stress_min
                ]
                self.current_filters['income_stress_min'] = income_stress_min
        
        if income_stress_max is not None:
            if 'income_stress_index' in self.filtered_data.columns:
                self.filtered_data = self.filtered_data[
                    self.filtered_data['income_stress_index'] <= income_stress_max
                ]
                self.current_filters['income_stress_max'] = income_stress_max
        
        if respiratory_cases_min is not None:
            if 'respiratory_cases' in self.filtered_data.columns:
                self.filtered_data = self.filtered_data[
                    self.filtered_data['respiratory_cases'] >= respiratory_cases_min
                ]
                self.current_filters['respiratory_cases_min'] = respiratory_cases_min
        
        if respiratory_cases_max is not None:
            if 'respiratory_cases' in self.filtered_data.columns:
                self.filtered_data = self.filtered_data[
                    self.filtered_data['respiratory_cases'] <= respiratory_cases_max
                ]
                self.current_filters['respiratory_cases_max'] = respiratory_cases_max
        
        return self.filtered_data
    
    def apply_statistical_filter(self, sample_size_min=None, data_completeness_min=None,
                               exclude_outliers=False):
        """
        Apply statistical filtering based on data quality metrics.
        
        Args:
            sample_size_min: Minimum sample size required
            data_completeness_min: Minimum data completeness (0-1)
            exclude_outliers: Whether to exclude statistical outliers
        """
        # Check if we have any data to work with
        if self.filtered_data is None or len(self.filtered_data) == 0:
            return self.filtered_data
        
        # Sample size filter with improved validation
        if sample_size_min is not None and sample_size_min > 0:
            if len(self.filtered_data) < sample_size_min:
                # If current data doesn't meet minimum, return empty DataFrame with same structure
                self.filtered_data = self.filtered_data.iloc[0:0].copy()
                self.current_filters['sample_size_min'] = sample_size_min
                return self.filtered_data
            self.current_filters['sample_size_min'] = sample_size_min
        
        # Data completeness filter with robust handling
        if data_completeness_min is not None and 0.0 <= data_completeness_min <= 1.0:
            try:
                # Calculate completeness for each row (excluding completely empty columns)
                non_empty_cols = []
                for col in self.filtered_data.columns:
                    if not self.filtered_data[col].isna().all():
                        non_empty_cols.append(col)
                
                if len(non_empty_cols) > 0:
                    # Calculate row-wise completeness
                    completeness = self.filtered_data[non_empty_cols].count(axis=1) / len(non_empty_cols)
                    # Filter rows that meet completeness threshold
                    mask = completeness >= data_completeness_min
                    self.filtered_data = self.filtered_data[mask]
                    self.current_filters['data_completeness_min'] = data_completeness_min
                else:
                    # If no non-empty columns, return empty dataset
                    self.filtered_data = self.filtered_data.iloc[0:0].copy()
            except Exception as e:
                # If completeness calculation fails, skip this filter
                pass
        
        # Outlier exclusion with robust error handling
        if exclude_outliers and len(self.filtered_data) > 10:  # Need sufficient data for outlier detection
            try:
                # Remove outliers using IQR method for key numeric columns
                key_columns = ['aqi', 'pm25', 'respiratory_cases']
                
                for col in key_columns:
                    if col in self.filtered_data.columns and len(self.filtered_data) > 10:
                        try:
                            # Get numeric data only
                            col_data = pd.to_numeric(self.filtered_data[col], errors='coerce')
                            col_data = col_data.dropna()
                            
                            if len(col_data) > 10:  # Need sufficient data for quartiles
                                Q1 = col_data.quantile(0.25)
                                Q3 = col_data.quantile(0.75)
                                IQR = Q3 - Q1
                                
                                # Only apply outlier removal if IQR is meaningful
                                if IQR > 0 and not pd.isna(IQR):
                                    lower_bound = Q1 - 1.5 * IQR
                                    upper_bound = Q3 + 1.5 * IQR
                                    
                                    # Create mask for non-outliers
                                    mask = (
                                        (pd.to_numeric(self.filtered_data[col], errors='coerce') >= lower_bound) & 
                                        (pd.to_numeric(self.filtered_data[col], errors='coerce') <= upper_bound)
                                    ) | pd.to_numeric(self.filtered_data[col], errors='coerce').isna()
                                    
                                    self.filtered_data = self.filtered_data[mask]
                        except Exception as e:
                            # Skip outlier removal for this column if there's an error
                            continue
                
                self.current_filters['exclude_outliers'] = exclude_outliers
            except Exception as e:
                # If outlier detection fails completely, skip it
                pass
        
        return self.filtered_data
    
    def get_filtered_dataset(self):
        """Get the current filtered dataset."""
        return self.filtered_data
    
    def get_available_filter_values(self):
        """
        Get available values for each filter category from the original data.
        
        Returns:
            Dictionary with available values for each filter type
        """
        if self.original_data is None:
            return {}
        
        available_values = {}
        
        # Location values
        if 'location' in self.original_data.columns:
            available_values['locations'] = sorted(self.original_data['location'].unique().tolist())
        
        # Age group values
        if 'age_group' in self.original_data.columns:
            available_values['age_groups'] = sorted(self.original_data['age_group'].unique().tolist())
        
        # Gender values
        if 'gender' in self.original_data.columns:
            available_values['genders'] = sorted(self.original_data['gender'].unique().tolist())
        
        # Season values
        if 'season' in self.original_data.columns:
            available_values['seasons'] = sorted(self.original_data['season'].unique().tolist())
        
        # Numeric ranges
        numeric_ranges = {}
        for col in ['aqi', 'pm25', 'respiratory_cases']:
            if col in self.original_data.columns:
                numeric_ranges[col] = {
                    'min': float(self.original_data[col].min()),
                    'max': float(self.original_data[col].max()),
                    'mean': float(self.original_data[col].mean())
                }
        available_values['numeric_ranges'] = numeric_ranges
        
        # Date range
        if 'date' in self.original_data.columns:
            date_col = pd.to_datetime(self.original_data['date'])
            available_values['date_range'] = {
                'min': date_col.min(),
                'max': date_col.max()
            }
        
        return available_values
    
    def reset_filters(self):
        """Reset all filters and return to original data."""
        if self.original_data is not None:
            self.filtered_data = self.original_data.copy()
        self.current_filters = {}
        return self.filtered_data
    
    def get_current_filters(self):
        """Get the currently applied filters."""
        return self.current_filters.copy()
    
    def validate_filter_combination(self, **filter_params):
        """
        Validate filter combination before applying to prevent empty results.
        
        Args:
            **filter_params: Filter parameters to validate
            
        Returns:
            Dictionary with validation results and warnings
        """
        validation_result = {
            'is_valid': True,
            'warnings': [],
            'estimated_retention': 1.0
        }
        
        if self.filtered_data is None or len(self.filtered_data) == 0:
            validation_result['is_valid'] = False
            validation_result['warnings'].append("No data available for filtering")
            return validation_result
        
        current_size = len(self.filtered_data)
        
        # Check sample size requirements
        sample_size_min = filter_params.get('sample_size_min', 0)
        if sample_size_min > current_size:
            validation_result['warnings'].append("Sample size requirement ({}) exceeds available data ({})".format(sample_size_min, current_size))
            validation_result['estimated_retention'] = 0.0
        
        # Check data completeness impact
        data_completeness_min = filter_params.get('data_completeness_min', 0.0)
        if data_completeness_min > 0.8:
            validation_result['warnings'].append("High completeness requirement may significantly reduce dataset")
        
        # Check for overly restrictive combinations
        active_filters = len(self.current_filters)
        if active_filters > 5:
            validation_result['warnings'].append("Many filters active - consider simplifying for better results")
        
        return validation_result
    
    def get_filter_summary(self):
        """
        Get a summary of current filtering status.
        
        Returns:
            Dictionary with filtering statistics
        """
        if self.original_data is None:
            return {}
        
        original_count = len(self.original_data)
        filtered_count = len(self.filtered_data) if self.filtered_data is not None else 0
        
        return {
            'original_records': original_count,
            'filtered_records': filtered_count,
            'records_removed': original_count - filtered_count,
            'retention_rate': filtered_count / original_count if original_count > 0 else 0,
            'active_filters': len(self.current_filters),
            'filter_details': self.current_filters.copy()
        }


def create_filter_chain(data, filters_config):
    """
    Create a filter chain and apply multiple filters in sequence.
    
    Args:
        data: Original DataFrame to filter
        filters_config: Dictionary with filter configurations
        
    Returns:
        Filtered DataFrame
    """
    filter_manager = FilterManager()
    filter_manager.set_data(data)
    
    # Apply filters in order
    if 'locations' in filters_config:
        filter_manager.apply_location_filter(filters_config['locations'])
    
    if 'demographics' in filters_config:
        demo = filters_config['demographics']
        filter_manager.apply_demographic_filter(
            age_groups=demo.get('age_groups'),
            genders=demo.get('genders')
        )
    
    if 'environmental' in filters_config:
        env = filters_config['environmental']
        filter_manager.apply_environmental_filter(
            seasons=env.get('seasons'),
            aqi_min=env.get('aqi_min'),
            aqi_max=env.get('aqi_max'),
            pm25_min=env.get('pm25_min'),
            pm25_max=env.get('pm25_max')
        )
    
    if 'temporal' in filters_config:
        temp = filters_config['temporal']
        filter_manager.apply_temporal_filter(
            start_date=temp.get('start_date'),
            end_date=temp.get('end_date')
        )
    
    if 'thresholds' in filters_config:
        thresh = filters_config['thresholds']
        filter_manager.apply_threshold_filter(
            income_stress_min=thresh.get('income_stress_min'),
            income_stress_max=thresh.get('income_stress_max'),
            respiratory_cases_min=thresh.get('respiratory_cases_min'),
            respiratory_cases_max=thresh.get('respiratory_cases_max')
        )
    
    if 'statistical' in filters_config:
        stat = filters_config['statistical']
        filter_manager.apply_statistical_filter(
            sample_size_min=stat.get('sample_size_min'),
            data_completeness_min=stat.get('data_completeness_min'),
            exclude_outliers=stat.get('exclude_outliers', False)
        )
    
    return filter_manager.get_filtered_dataset()


if __name__ == "__main__":
    # Test the FilterManager with sample data
    import pandas as pd
    import numpy as np
    
    # Create sample data
    np.random.seed(42)
    sample_data = pd.DataFrame({
        'date': pd.date_range('2023-01-01', periods=100, freq='D'),
        'location': np.random.choice(['City_A', 'City_B', 'City_C'], 100),
        'age_group': np.random.choice(['0-18', '19-35', '36-50', '51-65', '65+'], 100),
        'gender': np.random.choice(['Male', 'Female'], 100),
        'season': np.random.choice(['Spring', 'Summer', 'Fall', 'Winter'], 100),
        'aqi': np.random.randint(50, 200, 100),
        'pm25': np.random.uniform(10, 150, 100),
        'respiratory_cases': np.random.randint(1, 50, 100),
        'income_stress_index': np.random.uniform(500, 3000, 100)
    })
    
    print("Testing FilterManager...")
    print("Original data shape: {}".format(sample_data.shape))
    
    # Test basic filtering
    filter_manager = FilterManager()
    filter_manager.set_data(sample_data)
    
    # Test location filter
    filtered = filter_manager.apply_location_filter(['City_A', 'City_B'])
    print("After location filter: {}".format(filtered.shape))
    
    # Test demographic filter
    filtered = filter_manager.apply_demographic_filter(
        age_groups=['19-35', '36-50'], 
        genders=['Female']
    )
    print("After demographic filter: {}".format(filtered.shape))
    
    # Test environmental filter
    filtered = filter_manager.apply_environmental_filter(
        seasons=['Spring', 'Summer'],
        aqi_min=75,
        aqi_max=150
    )
    print("After environmental filter: {}".format(filtered.shape))
    
    # Get filter summary
    summary = filter_manager.get_filter_summary()
    print("Filter summary:")
    print("  Original records: {}".format(summary['original_records']))
    print("  Filtered records: {}".format(summary['filtered_records']))
    print("  Retention rate: {:.2%}".format(summary['retention_rate']))
    print("  Active filters: {}".format(summary['active_filters']))
    
    # Test available values
    available = filter_manager.get_available_filter_values()
    print("Available locations: {}".format(available.get('locations', [])))
    print("Available age groups: {}".format(available.get('age_groups', [])))
    
    print("FilterManager tests completed successfully!")