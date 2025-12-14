"""
Data processing module for the Air Quality vs Income Dashboard.

This module handles loading, merging, and processing of CSV data files,
including environmental data, hospitalization records, and income proxy data.
It provides statistical calculations, normalization, and data validation.
"""

import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import os
import logging

# Import data models
from models.data_models import (
    EnvironmentalData, HospitalizationData, IncomeProxyData, AnalysisData,
    validate_dataframe_schema, get_correlation_strength_label,
    ENVIRONMENTAL_SCHEMA, HOSPITALIZATION_SCHEMA, INCOME_PROXY_SCHEMA
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataProcessor:
    """
    Main data processing class for loading, merging, and analyzing datasets.
    """
    
    def __init__(self, data_directory: str = "data"):
        """
        Initialize the DataProcessor.
        
        Args:
            data_directory: Directory containing CSV files
        """
        self.data_directory = data_directory
        self.environmental_data = None
        self.hospitalization_data = None
        self.income_proxy_data = None
        self.merged_data = None
        
    def load_and_merge_datasets(self) -> pd.DataFrame:
        """
        Load all CSV datasets and merge them on date and location.
        
        Returns:
            Merged DataFrame with all data sources
            
        Raises:
            FileNotFoundError: If required CSV files are missing
            ValueError: If data validation fails
        """
        try:
            # Load individual datasets
            self.environmental_data = self._load_environmental_data()
            self.hospitalization_data = self._load_hospitalization_data()
            self.income_proxy_data = self._load_income_proxy_data()
            
            # Merge datasets on date and location
            self.merged_data = self._merge_datasets()
            
            logger.info("Successfully loaded and merged {} records".format(len(self.merged_data)))
            return self.merged_data
            
        except Exception as e:
            logger.error("Error loading and merging datasets: {}".format(str(e)))
            raise
    
    def _load_environmental_data(self) -> pd.DataFrame:
        """Load and validate environmental data from CSV."""
        file_path = os.path.join(self.data_directory, "aqi_env.csv")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError("Environmental data file not found: {}".format(file_path))
        
        df = pd.read_csv(file_path)
        validate_dataframe_schema(df, ENVIRONMENTAL_SCHEMA, "Environmental")
        
        # Convert date column to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Validate data ranges
        if (df['pm25'] < 0).any() or (df['pm10'] < 0).any():
            raise ValueError("PM values cannot be negative")
        if (df['aqi'] < 0).any() or (df['aqi'] > 500).any():
            raise ValueError("AQI values must be between 0 and 500")
            
        return df
    
    def _load_hospitalization_data(self) -> pd.DataFrame:
        """Load and validate hospitalization data from CSV."""
        file_path = os.path.join(self.data_directory, "hospital_cases.csv")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError("Hospitalization data file not found: {}".format(file_path))
        
        df = pd.read_csv(file_path)
        validate_dataframe_schema(df, HOSPITALIZATION_SCHEMA, "Hospitalization")
        
        # Convert date column to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Validate data ranges
        if (df['respiratory_cases'] < 0).any() or (df['hospital_days'] < 0).any():
            raise ValueError("Case counts and hospital days cannot be negative")
            
        return df
    
    def _load_income_proxy_data(self) -> pd.DataFrame:
        """Load and validate income proxy data from CSV."""
        file_path = os.path.join(self.data_directory, "income_proxy.csv")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError("Income proxy data file not found: {}".format(file_path))
        
        df = pd.read_csv(file_path)
        validate_dataframe_schema(df, INCOME_PROXY_SCHEMA, "Income proxy")
        
        # Convert date column to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Validate data ranges
        if (df['avg_daily_wage'] < 0).any() or (df['treatment_cost_est'] < 0).any():
            raise ValueError("Wage and cost values cannot be negative")
            
        return df
    
    def _merge_datasets(self) -> pd.DataFrame:
        """
        Merge all datasets on date and location fields.
        
        Returns:
            Merged DataFrame
        """
        # Start with environmental data as base
        merged = self.environmental_data.copy()
        
        # Merge with hospitalization data
        merged = merged.merge(
            self.hospitalization_data,
            on=['date', 'location'],
            how='inner'
        )
        
        # Merge with income proxy data
        merged = merged.merge(
            self.income_proxy_data,
            on=['date', 'location'],
            how='inner'
        )
        
        if merged.empty:
            raise ValueError("No matching records found across datasets")
        
        return merged
    
    def calculate_income_stress_index(self, df: pd.DataFrame = None) -> pd.Series:
        """
        Calculate Income Stress Index using the specified formula.
        
        Formula: stress = (hospital_days × avg_daily_wage) + treatment_cost_est
        
        Args:
            df: DataFrame to calculate for (uses merged_data if None)
            
        Returns:
            Series with Income Stress Index values
        """
        if df is None:
            df = self.merged_data
            
        if df is None:
            raise ValueError("No data available. Load datasets first.")
        
        # Apply the Income Stress Index formula
        stress_index = (df['hospital_days'] * df['avg_daily_wage']) + df['treatment_cost_est']
        
        return stress_index
    
    def normalize_values(self, series: pd.Series) -> pd.Series:
        """
        Apply min-max normalization to a series.
        
        Args:
            series: Series to normalize
            
        Returns:
            Normalized series with values between 0 and 1
        """
        min_val = series.min()
        max_val = series.max()
        
        # Handle edge case where all values are the same
        if min_val == max_val:
            return pd.Series([0.5] * len(series), index=series.index)
        
        normalized = (series - min_val) / (max_val - min_val)
        return normalized
    
    def calculate_correlations(self, x: pd.Series, y: pd.Series) -> Dict[str, float]:
        """
        Calculate Pearson correlation coefficient and p-value.
        
        Args:
            x: First variable series
            y: Second variable series
            
        Returns:
            Dictionary with correlation coefficient, p-value, and strength label
        """
        # Remove any NaN values
        valid_data = pd.DataFrame({'x': x, 'y': y}).dropna()
        
        if len(valid_data) < 2:
            raise ValueError("Insufficient data points for correlation calculation")
        
        # Calculate Pearson correlation
        correlation, p_value = stats.pearsonr(valid_data['x'], valid_data['y'])
        
        # Get strength label
        strength_label = get_correlation_strength_label(correlation)
        
        return {
            'correlation': correlation,
            'p_value': p_value,
            'strength': strength_label,
            'sample_size': len(valid_data)
        }
    
    def calculate_rolling_averages(self, series: pd.Series, window: int = 7) -> pd.Series:
        """
        Calculate rolling averages using pandas.
        
        Args:
            series: Time series data
            window: Rolling window size in days
            
        Returns:
            Series with rolling averages
        """
        return series.rolling(window=window, min_periods=1).mean()
    
    def calculate_high_aqi_percentage_increase(self, df: pd.DataFrame = None, 
                                            aqi_threshold: int = 100) -> float:
        """
        Calculate percentage increase in respiratory cases during high AQI periods.
        
        Args:
            df: DataFrame to analyze (uses merged_data if None)
            aqi_threshold: AQI threshold for "high" classification
            
        Returns:
            Percentage increase in respiratory cases
        """
        if df is None:
            df = self.merged_data
            
        if df is None:
            raise ValueError("No data available. Load datasets first.")
        
        # Split data into high and normal AQI periods
        high_aqi = df[df['aqi'] >= aqi_threshold]
        normal_aqi = df[df['aqi'] < aqi_threshold]
        
        if len(high_aqi) == 0 or len(normal_aqi) == 0:
            return 0.0
        
        # Calculate average respiratory cases for each period
        avg_high = high_aqi['respiratory_cases'].mean()
        avg_normal = normal_aqi['respiratory_cases'].mean()
        
        # Calculate percentage increase
        if avg_normal == 0:
            return 0.0
        
        percentage_increase = ((avg_high - avg_normal) / avg_normal) * 100
        return percentage_increase
    
    def get_data_completeness(self, df: pd.DataFrame = None) -> float:
        """
        Calculate data completeness as percentage of non-null values.
        
        Args:
            df: DataFrame to analyze (uses merged_data if None)
            
        Returns:
            Data completeness percentage (0-1)
        """
        if df is None:
            df = self.merged_data
            
        if df is None:
            return 0.0
        
        total_cells = df.size
        non_null_cells = df.count().sum()
        
        return non_null_cells / total_cells if total_cells > 0 else 0.0
    
    def detect_outliers(self, series: pd.Series, method: str = 'iqr') -> pd.Series:
        """
        Detect outliers in a series using specified method.
        
        Args:
            series: Series to analyze
            method: Method to use ('iqr' or 'zscore')
            
        Returns:
            Boolean series indicating outliers
        """
        if method == 'iqr':
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            return (series < lower_bound) | (series > upper_bound)
        
        elif method == 'zscore':
            z_scores = np.abs(stats.zscore(series.dropna()))
            return pd.Series(z_scores > 3, index=series.index).fillna(False)
        
        else:
            raise ValueError("Method must be 'iqr' or 'zscore'")


def create_sample_data(data_directory: str = "data") -> None:
    """
    Create sample CSV files for testing purposes.
    
    Args:
        data_directory: Directory to create sample files in
    """
    os.makedirs(data_directory, exist_ok=True)
    
    # Create sample environmental data
    env_data = {
        'date': pd.date_range('2023-01-01', periods=100, freq='D'),
        'location': ['City_A'] * 50 + ['City_B'] * 50,
        'pm25': np.random.uniform(10, 150, 100),
        'pm10': np.random.uniform(20, 200, 100),
        'aqi': np.random.randint(50, 200, 100),
        'temperature': np.random.uniform(-5, 35, 100),
        'wind_speed': np.random.uniform(0, 20, 100),
        'sunlight': np.random.uniform(0, 12, 100),
        'season': np.random.choice(['Spring', 'Summer', 'Fall', 'Winter'], 100)
    }
    pd.DataFrame(env_data).to_csv(os.path.join(data_directory, 'aqi_env.csv'), index=False)
    
    # Create sample hospitalization data
    hosp_data = {
        'date': pd.date_range('2023-01-01', periods=100, freq='D'),
        'location': ['City_A'] * 50 + ['City_B'] * 50,
        'age_group': np.random.choice(['0-18', '19-35', '36-50', '51-65', '65+'], 100),
        'gender': np.random.choice(['Male', 'Female'], 100),
        'respiratory_cases': np.random.randint(1, 50, 100),
        'hospital_days': np.random.randint(1, 10, 100)
    }
    pd.DataFrame(hosp_data).to_csv(os.path.join(data_directory, 'hospital_cases.csv'), index=False)
    
    # Create sample income proxy data
    income_data = {
        'date': pd.date_range('2023-01-01', periods=100, freq='D'),
        'location': ['City_A'] * 50 + ['City_B'] * 50,
        'avg_daily_wage': np.random.uniform(50, 300, 100),
        'treatment_cost_est': np.random.uniform(100, 2000, 100)
    }
    pd.DataFrame(income_data).to_csv(os.path.join(data_directory, 'income_proxy.csv'), index=False)
    
    logger.info("Sample data created in {} directory".format(data_directory))


if __name__ == "__main__":
    # Create sample data for testing
    create_sample_data()
    
    # Test the DataProcessor
    processor = DataProcessor()
    try:
        merged_data = processor.load_and_merge_datasets()
        print("Successfully loaded {} records".format(len(merged_data)))
        
        # Test Income Stress Index calculation
        stress_index = processor.calculate_income_stress_index()
        print("Income Stress Index range: {:.2f} - {:.2f}".format(stress_index.min(), stress_index.max()))
        
        # Test correlation calculation
        corr_result = processor.calculate_correlations(merged_data['aqi'], stress_index)
        print("AQI vs Stress correlation: {:.3f} ({})".format(corr_result['correlation'], corr_result['strength']))
        
    except Exception as e:
        print("Error: {}".format(e))