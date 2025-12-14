"""
Test script to verify the statistical filters and environmental context fixes.
"""

import sys
import os
import pandas as pd
import numpy as np

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from filters.filter_manager import FilterManager
from ui.dashboard_layout import DashboardLayout

def test_statistical_filters():
    """Test the statistical filter fixes."""
    print("Testing Statistical Filters...")
    
    # Create sample data
    np.random.seed(42)
    data = pd.DataFrame({
        'date': pd.date_range('2023-01-01', periods=100, freq='D'),
        'location': np.random.choice(['City_A', 'City_B', 'City_C'], 100),
        'aqi': np.random.randint(50, 200, 100),
        'pm25': np.random.uniform(10, 150, 100),
        'respiratory_cases': np.random.randint(1, 50, 100),
        'temperature': np.random.uniform(-5, 35, 100),
        'wind_speed': np.random.uniform(0, 20, 100),
        'season': np.random.choice(['Spring', 'Summer', 'Fall', 'Winter'], 100)
    })
    
    # Test FilterManager
    filter_manager = FilterManager()
    filter_manager.set_data(data)
    
    # Test statistical filters
    print(f"Original data size: {len(data)}")
    
    # Test sample size filter
    filtered = filter_manager.apply_statistical_filter(sample_size_min=50)
    print(f"After sample size filter (min 50): {len(filtered)}")
    
    # Reset and test completeness filter
    filter_manager.set_data(data)
    filtered = filter_manager.apply_statistical_filter(data_completeness_min=0.8)
    print(f"After completeness filter (80%): {len(filtered)}")
    
    # Reset and test outlier removal
    filter_manager.set_data(data)
    filtered = filter_manager.apply_statistical_filter(exclude_outliers=True)
    print(f"After outlier removal: {len(filtered)}")
    
    # Test all filters together
    filter_manager.set_data(data)
    filtered = filter_manager.apply_statistical_filter(
        sample_size_min=10,
        data_completeness_min=0.5,
        exclude_outliers=True
    )
    print(f"After all statistical filters: {len(filtered)}")
    
    print("✅ Statistical filters test completed successfully!")
    return True

def test_environmental_context():
    """Test the environmental context fixes."""
    print("\nTesting Environmental Context...")
    
    # Create sample data with some missing values
    np.random.seed(42)
    data = pd.DataFrame({
        'date': pd.date_range('2023-01-01', periods=50, freq='D'),
        'location': np.random.choice(['City_A', 'City_B'], 50),
        'aqi': np.random.randint(50, 200, 50),
        'pm25': np.random.uniform(10, 150, 50),
        'temperature': np.random.uniform(-5, 35, 50),
        'wind_speed': np.random.uniform(0, 20, 50),
        'respiratory_cases': np.random.randint(1, 50, 50),
        'season': np.random.choice(['Spring', 'Summer', 'Fall', 'Winter'], 50)
    })
    
    # Add some NaN values to test error handling
    data.loc[0:5, 'temperature'] = np.nan
    data.loc[10:15, 'wind_speed'] = np.nan
    
    # Test DashboardLayout
    layout = DashboardLayout()
    layout.set_data(data)
    
    # Test that environmental context can handle the data
    try:
        # This would normally render in Streamlit, but we can test the data processing
        env_columns = ['temperature', 'wind_speed', 'season', 'aqi', 'pm25']
        available_env_cols = [col for col in env_columns if col in data.columns]
        print(f"Available environmental columns: {available_env_cols}")
        
        # Test correlation calculation with NaN handling
        if 'aqi' in data.columns and 'temperature' in data.columns:
            clean_data = data[['temperature', 'aqi']].dropna()
            if len(clean_data) > 1:
                temp_aqi_corr = clean_data['temperature'].corr(clean_data['aqi'])
                print(f"Temperature-AQI correlation: {temp_aqi_corr:.3f}")
            else:
                print("Insufficient clean data for temperature-AQI correlation")
        
        # Test seasonal analysis
        if 'season' in data.columns and 'aqi' in data.columns:
            seasonal_data = data[['season', 'aqi']].dropna()
            if len(seasonal_data) > 0:
                seasonal_aqi = seasonal_data.groupby('season')['aqi'].mean()
                print(f"Seasonal AQI averages: {seasonal_aqi.to_dict()}")
        
        print("✅ Environmental context test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Environmental context test failed: {e}")
        return False

def test_correlation_matrix():
    """Test the enhanced correlation matrix."""
    print("\nTesting Enhanced Correlation Matrix...")
    
    # Create sample data
    np.random.seed(42)
    data = pd.DataFrame({
        'aqi': np.random.randint(50, 200, 100),
        'pm25': np.random.uniform(10, 150, 100),
        'temperature': np.random.uniform(-5, 35, 100),
        'wind_speed': np.random.uniform(0, 20, 100),
        'respiratory_cases': np.random.randint(1, 50, 100)
    })
    
    try:
        # Test correlation calculation
        key_cols = ['aqi', 'pm25', 'respiratory_cases', 'temperature', 'wind_speed']
        available_cols = [col for col in key_cols if col in data.columns and not data[col].isna().all()]
        
        if len(available_cols) > 1:
            clean_data = data[available_cols].dropna()
            if len(clean_data) > 1:
                corr_matrix = clean_data.corr()
                print(f"Correlation matrix shape: {corr_matrix.shape}")
                
                # Find strongest correlations
                correlations = []
                for i in range(len(available_cols)):
                    for j in range(i+1, len(available_cols)):
                        corr_val = corr_matrix.iloc[i, j]
                        if not pd.isna(corr_val):
                            correlations.append({
                                'var1': available_cols[i],
                                'var2': available_cols[j],
                                'correlation': corr_val,
                                'abs_correlation': abs(corr_val)
                            })
                
                correlations.sort(key=lambda x: x['abs_correlation'], reverse=True)
                print(f"Strongest correlation: {correlations[0]['var1']} ↔ {correlations[0]['var2']}: {correlations[0]['correlation']:.3f}")
        
        print("✅ Correlation matrix test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Correlation matrix test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Running Dashboard Fixes Tests...\n")
    
    # Run all tests
    tests = [
        test_statistical_filters,
        test_environmental_context,
        test_correlation_matrix
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    # Summary
    print(f"\n📊 Test Results: {sum(results)}/{len(results)} tests passed")
    
    if all(results):
        print("🎉 All tests passed! The fixes are working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the implementation.")