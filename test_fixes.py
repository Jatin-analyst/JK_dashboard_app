# -*- coding: utf-8 -*-
"""
Test script to verify the dashboard fixes work correctly.
"""

import sys
import os
import pandas as pd
import numpy as np

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported without errors."""
    print("Testing imports...")
    
    try:
        from data.real_data_processor import RealDataProcessor
        print("✓ RealDataProcessor imported successfully")
    except Exception as e:
        print("✗ RealDataProcessor import failed: {}".format(e))
        return False
    
    try:
        from ui.sidebar_filters import create_sidebar_filters
        print("✓ Sidebar filters imported successfully")
    except Exception as e:
        print("✗ Sidebar filters import failed: {}".format(e))
        return False
    
    try:
        from ui.dashboard_layout import create_dashboard_layout
        print("✓ Dashboard layout imported successfully")
    except Exception as e:
        print("✗ Dashboard layout import failed: {}".format(e))
        return False
    
    try:
        from filters.filter_manager import FilterManager
        print("✓ FilterManager imported successfully")
    except Exception as e:
        print("✗ FilterManager import failed: {}".format(e))
        return False
    
    return True

def test_filter_manager():
    """Test FilterManager with sample data."""
    print("\nTesting FilterManager...")
    
    try:
        from filters.filter_manager import FilterManager
        
        # Create sample data
        sample_data = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=10, freq='D'),
            'location': ['City_A'] * 5 + ['City_B'] * 5,
            'aqi': np.random.randint(50, 200, 10),
            'pm25': np.random.uniform(10, 150, 10),
            'respiratory_cases': np.random.randint(1, 50, 10)
        })
        
        # Test FilterManager
        fm = FilterManager()
        fm.set_data(sample_data)
        
        # Test filter summary
        summary = fm.get_filter_summary()
        print("✓ Filter summary generated: {} records".format(summary['filtered_records']))
        
        # Test location filter
        fm.apply_location_filter(['City_A'])
        filtered = fm.get_filtered_dataset()
        print("✓ Location filter applied: {} records".format(len(filtered)))
        
        # Test temporal filter
        fm.apply_temporal_filter(
            start_date=pd.to_datetime('2023-01-03'),
            end_date=pd.to_datetime('2023-01-07')
        )
        filtered = fm.get_filtered_dataset()
        print("✓ Temporal filter applied: {} records".format(len(filtered)))
        
        return True
        
    except Exception as e:
        print("✗ FilterManager test failed: {}".format(e))
        return False

def test_data_processor():
    """Test data processor with available data."""
    print("\nTesting RealDataProcessor...")
    
    try:
        from data.real_data_processor import RealDataProcessor
        
        processor = RealDataProcessor()
        
        # Check if data files exist
        data_files = ['city_day.csv', 'station_day.csv', 'stations.csv']
        available_files = []
        
        for file in data_files:
            if os.path.exists(os.path.join('data', file)):
                available_files.append(file)
        
        print("Available data files: {}".format(available_files))
        
        if len(available_files) > 0:
            try:
                processor.load_air_quality_data()
                print("✓ Air quality data loaded successfully")
                
                if processor.city_data is not None:
                    print("✓ City data available: {} records".format(len(processor.city_data)))
                
                return True
            except Exception as e:
                print("✗ Data loading failed: {}".format(e))
                return False
        else:
            print("ℹ No data files available for testing")
            return True
            
    except Exception as e:
        print("✗ RealDataProcessor test failed: {}".format(e))
        return False

def main():
    """Run all tests."""
    print("=== Dashboard Fix Verification ===\n")
    
    tests_passed = 0
    total_tests = 3
    
    if test_imports():
        tests_passed += 1
    
    if test_filter_manager():
        tests_passed += 1
    
    if test_data_processor():
        tests_passed += 1
    
    print("\n=== Test Results ===")
    print("Passed: {}/{}".format(tests_passed, total_tests))
    
    if tests_passed == total_tests:
        print("✓ All tests passed! Dashboard should work correctly.")
        return True
    else:
        print("✗ Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)