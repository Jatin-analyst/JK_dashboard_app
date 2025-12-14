"""
Property-based tests for data loading and merging functionality.

**Feature: air-quality-income-dashboard, Property 18: Data Loading and Merging Success**
**Validates: Requirements 6.1**
"""

import pytest
import pandas as pd
import numpy as np
from hypothesis import given, strategies as st, settings
from datetime import datetime, timedelta
import tempfile
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data.data_processor import DataProcessor
from models.data_models import (
    ENVIRONMENTAL_SCHEMA, HOSPITALIZATION_SCHEMA, INCOME_PROXY_SCHEMA
)


# Strategy for generating valid dates
date_strategy = st.datetimes(
    min_value=datetime(2020, 1, 1),
    max_value=datetime(2024, 12, 31)
).map(lambda dt: dt.date())

# Strategy for generating location names - use simple ASCII letters only
location_strategy = st.text(
    alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
    min_size=3,
    max_size=10
).filter(lambda x: x.strip() and not x.isspace() and x.lower() not in ['none', 'null', 'nan'])

# Strategy for generating seasons
season_strategy = st.sampled_from(['Spring', 'Summer', 'Fall', 'Winter'])

# Strategy for generating age groups
age_group_strategy = st.sampled_from(['0-18', '19-35', '36-50', '51-65', '65+'])

# Strategy for generating genders
gender_strategy = st.sampled_from(['Male', 'Female', 'Other'])


@st.composite
def environmental_data_strategy(draw):
    """Generate valid environmental data records."""
    size = draw(st.integers(min_value=5, max_value=50))
    dates = draw(st.lists(date_strategy, min_size=size, max_size=size))
    locations = draw(st.lists(location_strategy, min_size=size, max_size=size))
    
    return pd.DataFrame({
        'date': dates,
        'location': locations,
        'pm25': draw(st.lists(st.floats(min_value=0, max_value=500), min_size=size, max_size=size)),
        'pm10': draw(st.lists(st.floats(min_value=0, max_value=600), min_size=size, max_size=size)),
        'aqi': draw(st.lists(st.integers(min_value=0, max_value=500), min_size=size, max_size=size)),
        'temperature': draw(st.lists(st.floats(min_value=-40, max_value=50), min_size=size, max_size=size)),
        'wind_speed': draw(st.lists(st.floats(min_value=0, max_value=100), min_size=size, max_size=size)),
        'sunlight': draw(st.lists(st.floats(min_value=0, max_value=24), min_size=size, max_size=size)),
        'season': draw(st.lists(season_strategy, min_size=size, max_size=size))
    })


@st.composite
def hospitalization_data_strategy(draw, dates_locations):
    """Generate valid hospitalization data records matching dates and locations."""
    size = len(dates_locations)
    
    return pd.DataFrame({
        'date': [dl[0] for dl in dates_locations],
        'location': [dl[1] for dl in dates_locations],
        'age_group': draw(st.lists(age_group_strategy, min_size=size, max_size=size)),
        'gender': draw(st.lists(gender_strategy, min_size=size, max_size=size)),
        'respiratory_cases': draw(st.lists(st.integers(min_value=0, max_value=1000), min_size=size, max_size=size)),
        'hospital_days': draw(st.lists(st.integers(min_value=0, max_value=30), min_size=size, max_size=size))
    })


@st.composite
def income_proxy_data_strategy(draw, dates_locations):
    """Generate valid income proxy data records matching dates and locations."""
    size = len(dates_locations)
    
    return pd.DataFrame({
        'date': [dl[0] for dl in dates_locations],
        'location': [dl[1] for dl in dates_locations],
        'avg_daily_wage': draw(st.lists(st.floats(min_value=1, max_value=1000), min_size=size, max_size=size)),
        'treatment_cost_est': draw(st.lists(st.floats(min_value=1, max_value=10000), min_size=size, max_size=size))
    })


@st.composite
def matching_datasets_strategy(draw):
    """Generate three datasets with matching date/location keys."""
    env_data = draw(environmental_data_strategy())
    
    # Extract unique date/location combinations from environmental data
    dates_locations = list(zip(env_data['date'], env_data['location']))
    
    # Generate matching hospitalization and income data
    hosp_data = draw(hospitalization_data_strategy(dates_locations))
    income_data = draw(income_proxy_data_strategy(dates_locations))
    
    return env_data, hosp_data, income_data


class TestDataLoadingProperties:
    """Property-based tests for data loading and merging functionality."""
    
    @given(matching_datasets_strategy())
    @settings(max_examples=20, deadline=None)
    def test_data_loading_and_merging_success(self, datasets):
        """
        **Feature: air-quality-income-dashboard, Property 18: Data Loading and Merging Success**
        **Validates: Requirements 6.1**
        
        Property: For any valid CSV files matching the expected schema, 
        the dashboard should successfully load and merge all three datasets 
        (aqi_env.csv, hospital_cases.csv, income_proxy.csv) on date and location fields.
        """
        env_data, hosp_data, income_data = datasets
        
        # Create temporary directory and CSV files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save datasets as CSV files
            env_path = os.path.join(temp_dir, 'aqi_env.csv')
            hosp_path = os.path.join(temp_dir, 'hospital_cases.csv')
            income_path = os.path.join(temp_dir, 'income_proxy.csv')
            
            env_data.to_csv(env_path, index=False)
            hosp_data.to_csv(hosp_path, index=False)
            income_data.to_csv(income_path, index=False)
            
            # Initialize DataProcessor with temporary directory
            processor = DataProcessor(data_directory=temp_dir)
            
            # Load and merge datasets
            merged_data = processor.load_and_merge_datasets()
            
            # Verify successful loading and merging
            assert merged_data is not None, "Merged data should not be None"
            assert len(merged_data) > 0, "Merged data should not be empty"
            
            # Verify all required columns are present
            expected_columns = set(ENVIRONMENTAL_SCHEMA + HOSPITALIZATION_SCHEMA + INCOME_PROXY_SCHEMA)
            # Remove duplicate 'date' and 'location' columns
            expected_columns.discard('date')
            expected_columns.discard('location')
            expected_columns.update(['date', 'location'])
            
            actual_columns = set(merged_data.columns)
            assert expected_columns.issubset(actual_columns), f"Missing columns: {expected_columns - actual_columns}"
            
            # Verify data integrity - no null values in key columns
            assert merged_data['date'].notna().all(), "Date column should not have null values"
            assert merged_data['location'].notna().all(), "Location column should not have null values"
            
            # Verify data types
            assert pd.api.types.is_datetime64_any_dtype(merged_data['date']), "Date column should be datetime type"
            # Location column should be string-like (object or string dtype)
            assert merged_data['location'].dtype == 'object' or pd.api.types.is_string_dtype(merged_data['location']), "Location column should be string type"
            
            # Verify numeric columns are numeric
            numeric_columns = ['pm25', 'pm10', 'aqi', 'temperature', 'wind_speed', 
                             'sunlight', 'respiratory_cases', 'hospital_days', 
                             'avg_daily_wage', 'treatment_cost_est']
            for col in numeric_columns:
                if col in merged_data.columns:
                    assert pd.api.types.is_numeric_dtype(merged_data[col]), f"{col} should be numeric type"
            
            # Verify merge preserved data relationships
            # Each row in merged data should have matching date/location in all original datasets
            for _, row in merged_data.iterrows():
                date_val = row['date'].date() if hasattr(row['date'], 'date') else row['date']
                location_val = row['location']
                
                # Check environmental data match
                env_match = env_data[
                    (env_data['date'] == date_val) & 
                    (env_data['location'] == location_val)
                ]
                assert len(env_match) > 0, f"No environmental data match for {date_val}, {location_val}"
                
                # Check hospitalization data match
                hosp_match = hosp_data[
                    (hosp_data['date'] == date_val) & 
                    (hosp_data['location'] == location_val)
                ]
                assert len(hosp_match) > 0, f"No hospitalization data match for {date_val}, {location_val}"
                
                # Check income data match
                income_match = income_data[
                    (income_data['date'] == date_val) & 
                    (income_data['location'] == location_val)
                ]
                assert len(income_match) > 0, f"No income data match for {date_val}, {location_val}"


    @given(st.lists(st.text(min_size=1, max_size=10), min_size=1, max_size=5))
    @settings(max_examples=50)
    def test_missing_files_error_handling(self, filenames):
        """
        Property: For any non-existent file paths, the DataProcessor should raise 
        appropriate FileNotFoundError exceptions.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            processor = DataProcessor(data_directory=temp_dir)
            
            # Should raise FileNotFoundError when files don't exist
            with pytest.raises(FileNotFoundError):
                processor.load_and_merge_datasets()


    @given(environmental_data_strategy())
    @settings(max_examples=50)
    def test_schema_validation_environmental(self, env_data):
        """
        Property: For any DataFrame with valid environmental schema, 
        validation should pass without errors.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = os.path.join(temp_dir, 'aqi_env.csv')
            env_data.to_csv(env_path, index=False)
            
            processor = DataProcessor(data_directory=temp_dir)
            
            # Should successfully load environmental data
            loaded_env = processor._load_environmental_data()
            assert loaded_env is not None
            assert len(loaded_env) == len(env_data)
            
            # Verify all required columns are present
            for col in ENVIRONMENTAL_SCHEMA:
                assert col in loaded_env.columns, f"Missing required column: {col}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])