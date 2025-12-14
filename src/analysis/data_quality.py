"""
Data quality validation and reporting module.
"""

import pandas as pd
import numpy as np
import streamlit as st


def prepare_data_for_streamlit(df):
    """Prepare DataFrame for Streamlit display by fixing conversion issues."""
    if df is None or len(df) == 0:
        return df
    
    display_df = df.copy()
    
    # Fix datetime columns
    for col in display_df.columns:
        if pd.api.types.is_datetime64_any_dtype(display_df[col]):
            display_df[col] = display_df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    return display_df


class DataQualityValidator:
    """
    Validates data quality and generates quality reports.
    """
    
    def __init__(self):
        """Initialize the data quality validator."""
        self.quality_report = {}
    
    def validate_dataset(self, data, required_columns=None):
        """
        Perform comprehensive data quality validation.
        
        Args:
            data: DataFrame to validate
            required_columns: List of required column names
            
        Returns:
            Dictionary with validation results
        """
        if data is None or len(data) == 0:
            return {
                'is_valid': False,
                'error': 'Dataset is empty or None',
                'quality_score': 0.0
            }
        
        validation_results = {
            'is_valid': True,
            'total_records': len(data),
            'total_columns': len(data.columns),
            'issues': [],
            'warnings': [],
            'quality_metrics': {}
        }
        
        # Check required columns
        if required_columns:
            missing_cols = set(required_columns) - set(data.columns)
            if missing_cols:
                validation_results['is_valid'] = False
                validation_results['issues'].append(
                    "Missing required columns: {}".format(list(missing_cols))
                )
        
        # Check for completely empty columns
        empty_cols = data.columns[data.isnull().all()].tolist()
        if empty_cols:
            validation_results['warnings'].append(
                "Completely empty columns: {}".format(empty_cols)
            )
        
        # Calculate completeness metrics
        completeness = self._calculate_completeness(data)
        validation_results['quality_metrics']['completeness'] = completeness
        
        # Check for duplicates
        duplicate_info = self._check_duplicates(data)
        validation_results['quality_metrics']['duplicates'] = duplicate_info
        
        # Check data types and ranges
        type_info = self._validate_data_types(data)
        validation_results['quality_metrics']['data_types'] = type_info
        
        # Check for outliers
        outlier_info = self._detect_outliers(data)
        validation_results['quality_metrics']['outliers'] = outlier_info
        
        # Calculate overall quality score
        quality_score = self._calculate_quality_score(validation_results)
        validation_results['quality_score'] = quality_score
        
        self.quality_report = validation_results
        return validation_results
    
    def _calculate_completeness(self, data):
        """Calculate data completeness metrics."""
        total_cells = data.size
        non_null_cells = data.count().sum()
        overall_completeness = non_null_cells / total_cells if total_cells > 0 else 0
        
        # Per-column completeness
        column_completeness = (data.count() / len(data)).to_dict()
        
        # Identify columns with low completeness
        low_completeness_cols = [
            col for col, completeness in column_completeness.items() 
            if completeness < 0.8
        ]
        
        return {
            'overall_completeness': overall_completeness,
            'column_completeness': column_completeness,
            'low_completeness_columns': low_completeness_cols,
            'complete_records': len(data.dropna()),
            'incomplete_records': len(data) - len(data.dropna())
        }
    
    def _check_duplicates(self, data):
        """Check for duplicate records."""
        total_records = len(data)
        unique_records = len(data.drop_duplicates())
        duplicate_count = total_records - unique_records
        duplicate_percentage = (duplicate_count / total_records) * 100 if total_records > 0 else 0
        
        return {
            'total_records': total_records,
            'unique_records': unique_records,
            'duplicate_count': duplicate_count,
            'duplicate_percentage': duplicate_percentage,
            'has_duplicates': duplicate_count > 0
        }
    
    def _validate_data_types(self, data):
        """Validate data types and ranges for numeric columns."""
        type_info = {}
        
        for col in data.columns:
            col_info = {
                'dtype': str(data[col].dtype),
                'non_null_count': data[col].count(),
                'null_count': data[col].isnull().sum()
            }
            
            # Additional checks for numeric columns
            if pd.api.types.is_numeric_dtype(data[col]):
                col_info.update({
                    'min_value': data[col].min(),
                    'max_value': data[col].max(),
                    'mean_value': data[col].mean(),
                    'has_negative': (data[col] < 0).any(),
                    'has_zero': (data[col] == 0).any(),
                    'has_infinite': np.isinf(data[col]).any()
                })
                
                # Check for unrealistic values in specific columns
                if col.lower() in ['aqi']:
                    if data[col].min() < 0 or data[col].max() > 500:
                        col_info['range_warning'] = "AQI values outside expected range (0-500)"
                elif col.lower() in ['pm25', 'pm2.5']:
                    if data[col].min() < 0 or data[col].max() > 1000:
                        col_info['range_warning'] = "PM2.5 values outside typical range (0-1000)"
            
            # Check for date columns
            elif pd.api.types.is_datetime64_any_dtype(data[col]):
                col_info.update({
                    'min_date': data[col].min(),
                    'max_date': data[col].max(),
                    'date_range_days': (data[col].max() - data[col].min()).days
                })
            
            type_info[col] = col_info
        
        return type_info
    
    def _detect_outliers(self, data):
        """Detect outliers in numeric columns using IQR method."""
        outlier_info = {}
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            if data[col].count() > 0:  # Only process non-empty columns
                Q1 = data[col].quantile(0.25)
                Q3 = data[col].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = data[(data[col] < lower_bound) | (data[col] > upper_bound)][col]
                
                outlier_info[col] = {
                    'outlier_count': len(outliers),
                    'outlier_percentage': (len(outliers) / len(data)) * 100,
                    'lower_bound': lower_bound,
                    'upper_bound': upper_bound,
                    'has_outliers': len(outliers) > 0
                }
        
        return outlier_info
    
    def _calculate_quality_score(self, validation_results):
        """Calculate an overall data quality score (0-100)."""
        score = 100.0
        
        # Deduct points for issues
        if not validation_results['is_valid']:
            score -= 50
        
        # Deduct points for low completeness
        completeness = validation_results['quality_metrics']['completeness']['overall_completeness']
        if completeness < 0.9:
            score -= (0.9 - completeness) * 30
        
        # Deduct points for high duplicate percentage
        duplicate_pct = validation_results['quality_metrics']['duplicates']['duplicate_percentage']
        if duplicate_pct > 5:
            score -= min(duplicate_pct - 5, 20)
        
        # Deduct points for excessive outliers
        outlier_metrics = validation_results['quality_metrics']['outliers']
        avg_outlier_pct = np.mean([
            info['outlier_percentage'] for info in outlier_metrics.values()
        ]) if outlier_metrics else 0
        
        if avg_outlier_pct > 10:
            score -= min(avg_outlier_pct - 10, 15)
        
        return max(0, score)
    
    def generate_quality_report_display(self, validation_results=None):
        """
        Generate a Streamlit display for the data quality report.
        
        Args:
            validation_results: Validation results (uses stored report if None)
        """
        if validation_results is None:
            validation_results = self.quality_report
        
        if not validation_results:
            st.error("No quality report available. Run validation first.")
            return
        
        st.subheader("📊 Data Quality Report")
        
        # Overall quality score
        quality_score = validation_results.get('quality_score', 0)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Color code the quality score
            if quality_score >= 90:
                delta_color = "normal"
                score_color = "🟢"
            elif quality_score >= 70:
                delta_color = "normal"
                score_color = "🟡"
            else:
                delta_color = "inverse"
                score_color = "🔴"
            
            st.metric(
                "Quality Score",
                "{} {:.1f}/100".format(score_color, quality_score),
                help="Overall data quality assessment"
            )
        
        with col2:
            st.metric(
                "Total Records",
                "{:,}".format(validation_results.get('total_records', 0)),
                help="Number of records in dataset"
            )
        
        with col3:
            completeness = validation_results.get('quality_metrics', {}).get('completeness', {})
            overall_completeness = completeness.get('overall_completeness', 0)
            st.metric(
                "Data Completeness",
                "{:.1%}".format(overall_completeness),
                help="Percentage of non-null values"
            )
        
        # Issues and warnings
        if validation_results.get('issues'):
            st.error("**Issues Found:**")
            for issue in validation_results['issues']:
                st.error("• " + issue)
        
        if validation_results.get('warnings'):
            st.warning("**Warnings:**")
            for warning in validation_results['warnings']:
                st.warning("• " + warning)
        
        # Detailed metrics
        with st.expander("📈 Detailed Quality Metrics"):
            
            # Completeness details
            st.write("**Completeness by Column:**")
            completeness_data = completeness.get('column_completeness', {})
            if completeness_data:
                completeness_df = pd.DataFrame([
                    {'Column': col, 'Completeness': '{:.1%}'.format(comp)}
                    for col, comp in completeness_data.items()
                ])
                st.dataframe(prepare_data_for_streamlit(completeness_df), use_container_width=True)
            
            # Duplicate information
            duplicate_info = validation_results.get('quality_metrics', {}).get('duplicates', {})
            if duplicate_info:
                st.write("**Duplicate Records:**")
                st.write("• Duplicate records: {:,} ({:.1f}%)".format(
                    duplicate_info.get('duplicate_count', 0),
                    duplicate_info.get('duplicate_percentage', 0)
                ))
            
            # Outlier information
            outlier_info = validation_results.get('quality_metrics', {}).get('outliers', {})
            if outlier_info:
                st.write("**Outliers by Column:**")
                outlier_data = []
                for col, info in outlier_info.items():
                    if info['has_outliers']:
                        outlier_data.append({
                            'Column': col,
                            'Outlier_Count': info['outlier_count'],
                            'Outlier_Percentage': '{:.1f}%'.format(info['outlier_percentage'])
                        })
                
                if outlier_data:
                    outlier_df = pd.DataFrame(outlier_data)
                    st.dataframe(prepare_data_for_streamlit(outlier_df), use_container_width=True)
                else:
                    st.success("No significant outliers detected")
    
    def get_quality_summary(self):
        """Get a brief quality summary."""
        if not self.quality_report:
            return "No quality report available"
        
        score = self.quality_report.get('quality_score', 0)
        completeness = self.quality_report.get('quality_metrics', {}).get('completeness', {}).get('overall_completeness', 0)
        
        if score >= 90:
            quality_level = "Excellent"
        elif score >= 70:
            quality_level = "Good"
        elif score >= 50:
            quality_level = "Fair"
        else:
            quality_level = "Poor"
        
        return "Data Quality: {} (Score: {:.1f}/100, Completeness: {:.1%})".format(
            quality_level, score, completeness
        )


def validate_dashboard_data(data):
    """
    Convenience function to validate dashboard data.
    
    Args:
        data: DataFrame to validate
        
    Returns:
        DataQualityValidator instance with results
    """
    required_columns = ['date', 'location', 'aqi', 'pm25', 'respiratory_cases', 'income_stress_index']
    
    validator = DataQualityValidator()
    validation_results = validator.validate_dataset(data, required_columns)
    
    return validator, validation_results


if __name__ == "__main__":
    # Test the data quality validator
    import pandas as pd
    import numpy as np
    
    # Create sample data with quality issues
    np.random.seed(42)
    
    # Create base data
    base_aqi = np.random.randint(50, 200, 98)
    outlier_aqi = np.array([600, -10])  # Add outliers
    all_aqi = np.concatenate([base_aqi, outlier_aqi])
    
    sample_data = pd.DataFrame({
        'date': pd.date_range('2023-01-01', periods=100, freq='D'),
        'location': np.random.choice(['City_A', 'City_B', None], 100, p=[0.4, 0.4, 0.2]),
        'aqi': all_aqi,
        'pm25': np.random.uniform(10, 150, 100),
        'respiratory_cases': np.random.randint(1, 50, 100),
        'income_stress_index': np.random.uniform(500, 3000, 100),
        'empty_column': [None] * 100
    })
    
    # Add some duplicates
    sample_data = pd.concat([sample_data, sample_data.head(5)], ignore_index=True)
    
    print("Testing Data Quality Validator")
    print("=" * 40)
    
    validator = DataQualityValidator()
    results = validator.validate_dataset(sample_data)
    
    print("Validation Results:")
    print("  Valid: {}".format(results['is_valid']))
    print("  Quality Score: {:.1f}/100".format(results['quality_score']))
    print("  Total Records: {}".format(results['total_records']))
    print("  Issues: {}".format(len(results['issues'])))
    print("  Warnings: {}".format(len(results['warnings'])))
    
    completeness = results['quality_metrics']['completeness']
    print("  Overall Completeness: {:.1%}".format(completeness['overall_completeness']))
    
    duplicates = results['quality_metrics']['duplicates']
    print("  Duplicate Records: {} ({:.1f}%)".format(
        duplicates['duplicate_count'], duplicates['duplicate_percentage']
    ))
    
    print("\nQuality Summary: {}".format(validator.get_quality_summary()))
    
    print("\nData quality validation test completed successfully!")