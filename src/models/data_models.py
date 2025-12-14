"""
Data models for the Air Quality vs Income Dashboard.

This module defines the core data structures used throughout the application,
including environmental data, hospitalization records, income proxy data,
and merged analysis datasets.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple, Optional
import pandas as pd


@dataclass
class EnvironmentalData:
    """Environmental data model for air quality and weather information."""
    date: datetime
    location: str
    pm25: float
    pm10: float
    aqi: int
    temperature: float
    wind_speed: float
    sunlight: float
    season: str
    
    def __post_init__(self):
        """Validate environmental data after initialization."""
        if self.pm25 < 0 or self.pm10 < 0:
            raise ValueError("PM values cannot be negative")
        if self.aqi < 0 or self.aqi > 500:
            raise ValueError("AQI must be between 0 and 500")
        if self.season not in ['Spring', 'Summer', 'Fall', 'Winter']:
            raise ValueError("Season must be one of: Spring, Summer, Fall, Winter")


@dataclass
class HospitalizationData:
    """Hospitalization data model for respiratory health information."""
    date: datetime
    location: str
    age_group: str
    gender: str
    respiratory_cases: int
    hospital_days: int
    
    def __post_init__(self):
        """Validate hospitalization data after initialization."""
        if self.respiratory_cases < 0:
            raise ValueError("Respiratory cases cannot be negative")
        if self.hospital_days < 0:
            raise ValueError("Hospital days cannot be negative")
        if self.gender not in ['Male', 'Female', 'Other']:
            raise ValueError("Gender must be one of: Male, Female, Other")


@dataclass
class IncomeProxyData:
    """Income proxy data model for economic stress indicators."""
    date: datetime
    location: str
    avg_daily_wage: float
    treatment_cost_est: float
    
    def __post_init__(self):
        """Validate income proxy data after initialization."""
        if self.avg_daily_wage < 0:
            raise ValueError("Average daily wage cannot be negative")
        if self.treatment_cost_est < 0:
            raise ValueError("Treatment cost estimate cannot be negative")


@dataclass
class AnalysisData:
    """Merged analysis data model combining all data sources."""
    date: datetime
    location: str
    region: str
    urban_rural: str
    pm25: float
    aqi: int
    respiratory_cases: int
    income_stress_index: float
    normalized_aqi: float
    normalized_stress: float
    correlation_coefficient: float
    confidence_interval: Tuple[float, float]
    sample_size: int
    data_completeness: float
    
    def __post_init__(self):
        """Validate analysis data after initialization."""
        if not (0 <= self.normalized_aqi <= 1):
            raise ValueError("Normalized AQI must be between 0 and 1")
        if not (0 <= self.normalized_stress <= 1):
            raise ValueError("Normalized stress must be between 0 and 1")
        if not (-1 <= self.correlation_coefficient <= 1):
            raise ValueError("Correlation coefficient must be between -1 and 1")
        if not (0 <= self.data_completeness <= 1):
            raise ValueError("Data completeness must be between 0 and 1")


@dataclass
class FilterParameters:
    """Filter parameters for dashboard data filtering."""
    locations: List[str]
    regions: List[str]
    age_groups: List[str]
    genders: List[str]
    seasons: List[str]
    date_range: Tuple[datetime, datetime]
    aqi_threshold_min: float
    aqi_threshold_max: float
    income_threshold_min: float
    income_threshold_max: float
    correlation_strength_min: float
    sample_size_min: int
    data_completeness_min: float
    exclude_outliers: bool
    
    def __post_init__(self):
        """Validate filter parameters after initialization."""
        if self.date_range[0] > self.date_range[1]:
            raise ValueError("Start date must be before end date")
        if self.aqi_threshold_min > self.aqi_threshold_max:
            raise ValueError("AQI min threshold must be <= max threshold")
        if self.income_threshold_min > self.income_threshold_max:
            raise ValueError("Income min threshold must be <= max threshold")
        if not (0 <= self.correlation_strength_min <= 1):
            raise ValueError("Correlation strength min must be between 0 and 1")
        if self.sample_size_min < 1:
            raise ValueError("Sample size minimum must be at least 1")


def validate_dataframe_schema(df: pd.DataFrame, expected_columns: List[str], 
                            data_type: str) -> bool:
    """
    Validate that a DataFrame has the expected schema.
    
    Args:
        df: DataFrame to validate
        expected_columns: List of expected column names
        data_type: Type of data for error messages
        
    Returns:
        True if schema is valid
        
    Raises:
        ValueError: If schema validation fails
    """
    missing_columns = set(expected_columns) - set(df.columns)
    if missing_columns:
        raise ValueError(f"{data_type} data missing required columns: {missing_columns}")
    
    # Check for empty DataFrame
    if df.empty:
        raise ValueError(f"{data_type} data is empty")
    
    return True


def get_correlation_strength_label(correlation: float) -> str:
    """
    Classify correlation strength based on absolute value.
    
    Args:
        correlation: Correlation coefficient between -1 and 1
        
    Returns:
        String label: 'Weak', 'Moderate', or 'Strong'
    """
    abs_corr = abs(correlation)
    if abs_corr < 0.3:
        return 'Weak'
    elif abs_corr < 0.7:
        return 'Moderate'
    else:
        return 'Strong'


# Schema definitions for CSV validation
ENVIRONMENTAL_SCHEMA = [
    'date', 'location', 'pm25', 'pm10', 'aqi', 
    'temperature', 'wind_speed', 'sunlight', 'season'
]

HOSPITALIZATION_SCHEMA = [
    'date', 'location', 'age_group', 'gender', 
    'respiratory_cases', 'hospital_days'
]

INCOME_PROXY_SCHEMA = [
    'date', 'location', 'avg_daily_wage', 'treatment_cost_est'
]