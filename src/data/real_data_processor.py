"""
Real data processor for the Air Quality vs Income Dashboard.
Uses actual air quality data and generates correlated health/economic data.
"""

import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealDataProcessor:
    """
    Data processor that uses real air quality data and generates correlated synthetic data.
    """
    
    def __init__(self, data_directory="data"):
        """Initialize the processor."""
        self.data_directory = data_directory
        self.city_data = None
        self.station_data = None
        self.stations_info = None
        self.merged_data = None
    
    def load_air_quality_data(self):
        """Load real air quality data from CSV files."""
        try:
            # Load city-level daily data
            city_file = os.path.join(self.data_directory, "city_day.csv")
            if os.path.exists(city_file):
                self.city_data = pd.read_csv(city_file)
                self.city_data['Datetime'] = pd.to_datetime(self.city_data['Datetime'])
                logger.info("Loaded city data: {} records".format(len(self.city_data)))
            
            # Load station-level daily data
            station_file = os.path.join(self.data_directory, "station_day.csv")
            if os.path.exists(station_file):
                self.station_data = pd.read_csv(station_file)
                self.station_data['Datetime'] = pd.to_datetime(self.station_data['Datetime'])
                logger.info("Loaded station data: {} records".format(len(self.station_data)))
            
            # Load stations info
            stations_file = os.path.join(self.data_directory, "stations.csv")
            if os.path.exists(stations_file):
                self.stations_info = pd.read_csv(stations_file)
                logger.info("Loaded stations info: {} stations".format(len(self.stations_info)))
            
            return True
            
        except Exception as e:
            logger.error("Error loading air quality data: {}".format(str(e)))
            return False
    
    def generate_correlated_health_data(self, air_quality_df):
        """
        Generate synthetic health data that correlates with air quality.
        
        Args:
            air_quality_df: DataFrame with air quality data
            
        Returns:
            DataFrame with health data
        """
        np.random.seed(42)  # For reproducible results
        
        health_data = []
        
        for _, row in air_quality_df.iterrows():
            # Base respiratory cases influenced by AQI
            aqi = row['aqi']
            pm25 = row['pm25']
            
            # Higher AQI leads to more respiratory cases (with some randomness)
            base_cases = max(1, int((aqi / 50) * 5 + np.random.normal(0, 2)))
            
            # PM2.5 also influences cases
            pm25_factor = max(0.5, pm25 / 100)
            respiratory_cases = max(1, int(base_cases * pm25_factor))
            
            # Hospital days correlate with severity
            if aqi > 200:  # Severe
                hospital_days = np.random.randint(3, 8)
            elif aqi > 100:  # Moderate to Poor
                hospital_days = np.random.randint(2, 5)
            else:  # Good to Satisfactory
                hospital_days = np.random.randint(1, 3)
            
            # Generate multiple demographic records per day/location
            age_groups = ['0-18', '19-35', '36-50', '51-65', '65+']
            genders = ['Male', 'Female']
            
            for age_group in np.random.choice(age_groups, size=2, replace=False):
                for gender in np.random.choice(genders, size=1):
                    # Adjust cases by demographics
                    demo_cases = respiratory_cases
                    if age_group in ['0-18', '65+']:  # More vulnerable groups
                        demo_cases = int(demo_cases * 1.3)
                    
                    health_record = {
                        'date': row['date'],
                        'location': row['location'],
                        'age_group': age_group,
                        'gender': gender[0],
                        'respiratory_cases': max(1, demo_cases + np.random.randint(-2, 3)),
                        'hospital_days': hospital_days + np.random.randint(-1, 2)
                    }
                    health_data.append(health_record)
        
        return pd.DataFrame(health_data)
    
    def generate_correlated_income_data(self, air_quality_df):
        """
        Generate synthetic income data that correlates with air quality and location.
        
        Args:
            air_quality_df: DataFrame with air quality data
            
        Returns:
            DataFrame with income proxy data
        """
        np.random.seed(42)
        
        # City-based wage multipliers (reflecting economic differences)
        city_wage_multipliers = {
            'Delhi': 1.2,
            'Mumbai': 1.4,
            'Bangalore': 1.3,
            'Chennai': 1.1,
            'Kolkata': 1.0
        }
        
        income_data = []
        
        for _, row in air_quality_df.iterrows():
            city = row['location']
            aqi = row['aqi']
            
            # Base daily wage varies by city
            base_wage = 200 * city_wage_multipliers.get(city, 1.0)
            
            # Add some randomness
            avg_daily_wage = base_wage + np.random.normal(0, 50)
            avg_daily_wage = max(100, avg_daily_wage)  # Minimum wage floor
            
            # Treatment costs increase with pollution severity
            if aqi > 200:  # Severe
                base_treatment = np.random.uniform(1500, 3000)
            elif aqi > 100:  # Moderate to Poor
                base_treatment = np.random.uniform(800, 2000)
            else:  # Good to Satisfactory
                base_treatment = np.random.uniform(300, 1200)
            
            # City factor for treatment costs
            treatment_cost_est = base_treatment * city_wage_multipliers.get(city, 1.0)
            
            income_record = {
                'date': row['date'],
                'location': city,
                'avg_daily_wage': avg_daily_wage,
                'treatment_cost_est': treatment_cost_est
            }
            income_data.append(income_record)
        
        return pd.DataFrame(income_data)
    
    def add_weather_and_seasonal_data(self, df):
        """
        Add synthetic weather and seasonal data to the DataFrame.
        
        Args:
            df: DataFrame to add weather data to
            
        Returns:
            DataFrame with weather columns added
        """
        np.random.seed(42)
        
        # Add season based on date
        def get_season(date):
            month = date.month
            if month in [12, 1, 2]:
                return 'Winter'
            elif month in [3, 4, 5]:
                return 'Spring'
            elif month in [6, 7, 8]:
                return 'Summer'
            else:
                return 'Fall'
        
        df['season'] = df['date'].apply(get_season)
        
        # Generate correlated weather data
        weather_data = []
        for _, row in df.iterrows():
            # Temperature varies by season and affects air quality
            season = row['season']
            if season == 'Summer':
                temp = np.random.uniform(25, 40)
            elif season == 'Winter':
                temp = np.random.uniform(5, 20)
            else:  # Spring/Fall
                temp = np.random.uniform(15, 30)
            
            # Wind speed inversely correlates with pollution
            aqi = row['aqi']
            base_wind = max(2, 15 - (aqi / 50))  # Higher AQI = lower wind
            wind_speed = max(0, base_wind + np.random.normal(0, 3))
            
            # Sunlight hours
            sunlight = np.random.uniform(4, 12)
            
            weather_data.append({
                'temperature': temp,
                'wind_speed': wind_speed,
                'sunlight': sunlight
            })
        
        weather_df = pd.DataFrame(weather_data)
        return pd.concat([df, weather_df], axis=1)
    
    def create_comprehensive_dataset(self):
        """
        Create a comprehensive dataset combining real air quality data with synthetic health/economic data.
        
        Returns:
            Merged DataFrame with all required columns
        """
        if not self.load_air_quality_data():
            raise Exception("Failed to load air quality data")
        
        if self.city_data is None:
            raise Exception("No city air quality data available")
        
        # Use city-level data as base (more manageable size)
        base_data = self.city_data.copy()
        
        # Rename columns to match our schema
        base_data = base_data.rename(columns={
            'City': 'location',
            'Datetime': 'date',
            'PM2.5': 'pm25',
            'PM10': 'pm10',
            'AQI': 'aqi'
        })
        
        # Ensure date column is datetime
        base_data['date'] = pd.to_datetime(base_data['date'])
        
        # Add weather and seasonal data
        base_data = self.add_weather_and_seasonal_data(base_data)
        
        # Generate correlated health data
        logger.info("Generating correlated health data...")
        health_data = self.generate_correlated_health_data(base_data)
        
        # Generate correlated income data
        logger.info("Generating correlated income data...")
        income_data = self.generate_correlated_income_data(base_data)
        
        # Merge all datasets
        logger.info("Merging datasets...")
        
        # First merge base air quality with health data
        merged = base_data.merge(
            health_data,
            on=['date', 'location'],
            how='inner'
        )
        
        # Then merge with income data
        merged = merged.merge(
            income_data,
            on=['date', 'location'],
            how='inner'
        )
        
        # Calculate Income Stress Index
        merged['income_stress_index'] = (
            merged['hospital_days'] * merged['avg_daily_wage']
        ) + merged['treatment_cost_est']
        
        # Add region information (simplified)
        region_mapping = {
            'Delhi': 'North India',
            'Mumbai': 'West India',
            'Bangalore': 'South India',
            'Chennai': 'South India',
            'Kolkata': 'East India'
        }
        merged['region'] = merged['location'].map(region_mapping)
        
        # Add urban/rural classification (all major cities are urban)
        merged['urban_rural'] = 'Urban'
        
        self.merged_data = merged
        logger.info("Created comprehensive dataset with {} records".format(len(merged)))
        
        return merged
    
    def get_data_summary(self):
        """Get a summary of the loaded data."""
        if self.merged_data is None:
            return "No data loaded"
        
        summary = {
            'total_records': len(self.merged_data),
            'date_range': (
                self.merged_data['date'].min().strftime('%Y-%m-%d'),
                self.merged_data['date'].max().strftime('%Y-%m-%d')
            ),
            'cities': self.merged_data['location'].unique().tolist(),
            'aqi_range': (
                self.merged_data['aqi'].min(),
                self.merged_data['aqi'].max()
            ),
            'pm25_range': (
                self.merged_data['pm25'].min(),
                self.merged_data['pm25'].max()
            ),
            'income_stress_range': (
                self.merged_data['income_stress_index'].min(),
                self.merged_data['income_stress_index'].max()
            )
        }
        
        return summary
    
    def calculate_income_stress_index(self, df=None):
        """Calculate Income Stress Index using the specified formula."""
        if df is None:
            df = self.merged_data
        
        if df is None:
            raise ValueError("No data available. Load datasets first.")
        
        return (df['hospital_days'] * df['avg_daily_wage']) + df['treatment_cost_est']
    
    def normalize_values(self, series):
        """Apply min-max normalization to a series."""
        min_val = series.min()
        max_val = series.max()
        
        if min_val == max_val:
            return pd.Series([0.5] * len(series), index=series.index)
        
        return (series - min_val) / (max_val - min_val)
    
    def calculate_correlations(self, x, y):
        """Calculate Pearson correlation coefficient and p-value."""
        valid_data = pd.DataFrame({'x': x, 'y': y}).dropna()
        
        if len(valid_data) < 2:
            raise ValueError("Insufficient data points for correlation calculation")
        
        correlation, p_value = stats.pearsonr(valid_data['x'], valid_data['y'])
        
        abs_corr = abs(correlation)
        if abs_corr < 0.3:
            strength_label = 'Weak'
        elif abs_corr < 0.7:
            strength_label = 'Moderate'
        else:
            strength_label = 'Strong'
        
        return {
            'correlation': correlation,
            'p_value': p_value,
            'strength': strength_label,
            'sample_size': len(valid_data)
        }


def test_real_data_processor():
    """Test the real data processor."""
    processor = RealDataProcessor()
    
    try:
        # Create comprehensive dataset
        data = processor.create_comprehensive_dataset()
        
        # Get summary
        summary = processor.get_data_summary()
        
        print("Real Data Processor Test Results:")
        print("=" * 50)
        print("Total records: {}".format(summary['total_records']))
        print("Date range: {} to {}".format(*summary['date_range']))
        print("Cities: {}".format(', '.join(summary['cities'])))
        print("AQI range: {:.1f} - {:.1f}".format(*summary['aqi_range']))
        print("PM2.5 range: {:.1f} - {:.1f}".format(*summary['pm25_range']))
        print("Income Stress range: {:.0f} - {:.0f}".format(*summary['income_stress_range']))
        
        # Test correlations
        aqi_stress_corr = processor.calculate_correlations(
            data['aqi'], data['income_stress_index']
        )
        print("\nAQI vs Income Stress correlation: {:.3f} ({})".format(
            aqi_stress_corr['correlation'], aqi_stress_corr['strength']
        ))
        
        pm25_stress_corr = processor.calculate_correlations(
            data['pm25'], data['income_stress_index']
        )
        print("PM2.5 vs Income Stress correlation: {:.3f} ({})".format(
            pm25_stress_corr['correlation'], pm25_stress_corr['strength']
        ))
        
        # Show sample data
        print("\nSample data (first 5 records):")
        print(data[['date', 'location', 'aqi', 'pm25', 'respiratory_cases', 'income_stress_index']].head())
        
        return data
        
    except Exception as e:
        print("Error testing real data processor: {}".format(str(e)))
        return None


if __name__ == "__main__":
    test_real_data_processor()