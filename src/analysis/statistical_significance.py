"""
Statistical significance analysis module.
"""

import pandas as pd
import numpy as np
from scipy import stats
import math


class StatisticalSignificance:
    """
    Handles statistical significance calculations and confidence intervals.
    """
    
    def __init__(self):
        """Initialize the statistical significance analyzer."""
        pass
    
    def calculate_correlation_significance(self, x, y, confidence_level=0.95):
        """
        Calculate correlation with statistical significance and confidence intervals.
        
        Args:
            x: First variable series
            y: Second variable series
            confidence_level: Confidence level (default 0.95 for 95%)
            
        Returns:
            Dictionary with correlation statistics
        """
        # Remove NaN values
        valid_data = pd.DataFrame({'x': x, 'y': y}).dropna()
        
        if len(valid_data) < 3:
            return {
                'correlation': np.nan,
                'p_value': np.nan,
                'confidence_interval': (np.nan, np.nan),
                'is_significant': False,
                'sample_size': len(valid_data),
                'error': 'Insufficient data points'
            }
        
        # Calculate Pearson correlation
        correlation, p_value = stats.pearsonr(valid_data['x'], valid_data['y'])
        
        # Calculate confidence interval for correlation
        n = len(valid_data)
        alpha = 1 - confidence_level
        
        # Fisher's z-transformation for confidence interval
        if abs(correlation) < 0.999:  # Avoid division by zero
            z_r = 0.5 * math.log((1 + correlation) / (1 - correlation))
            se_z = 1 / math.sqrt(n - 3)
            z_critical = stats.norm.ppf(1 - alpha/2)
            
            z_lower = z_r - z_critical * se_z
            z_upper = z_r + z_critical * se_z
            
            # Transform back to correlation scale
            r_lower = (math.exp(2 * z_lower) - 1) / (math.exp(2 * z_lower) + 1)
            r_upper = (math.exp(2 * z_upper) - 1) / (math.exp(2 * z_upper) + 1)
            
            confidence_interval = (r_lower, r_upper)
        else:
            confidence_interval = (correlation * 0.95, correlation * 1.05)
        
        # Determine significance
        is_significant = p_value < (1 - confidence_level)
        
        # Get strength label
        abs_corr = abs(correlation)
        if abs_corr < 0.3:
            strength = 'Weak'
        elif abs_corr < 0.7:
            strength = 'Moderate'
        else:
            strength = 'Strong'
        
        return {
            'correlation': correlation,
            'p_value': p_value,
            'confidence_interval': confidence_interval,
            'is_significant': is_significant,
            'significance_level': 1 - confidence_level,
            'sample_size': n,
            'strength': strength,
            'confidence_level': confidence_level
        }
    
    def get_significance_badge(self, p_value, alpha=0.05):
        """
        Get a significance badge based on p-value.
        
        Args:
            p_value: P-value from statistical test
            alpha: Significance threshold (default 0.05)
            
        Returns:
            Dictionary with badge information
        """
        if pd.isna(p_value):
            return {
                'badge': 'N/A',
                'color': 'gray',
                'description': 'Not available'
            }
        
        if p_value < 0.001:
            return {
                'badge': '***',
                'color': 'darkgreen',
                'description': 'Highly significant (p < 0.001)'
            }
        elif p_value < 0.01:
            return {
                'badge': '**',
                'color': 'green',
                'description': 'Very significant (p < 0.01)'
            }
        elif p_value < alpha:
            return {
                'badge': '*',
                'color': 'lightgreen',
                'description': 'Significant (p < {})'.format(alpha)
            }
        else:
            return {
                'badge': 'ns',
                'color': 'red',
                'description': 'Not significant (p ≥ {})'.format(alpha)
            }
    
    def calculate_effect_size(self, x, y):
        """
        Calculate effect size (Cohen's conventions for correlation).
        
        Args:
            x: First variable
            y: Second variable
            
        Returns:
            Dictionary with effect size information
        """
        valid_data = pd.DataFrame({'x': x, 'y': y}).dropna()
        
        if len(valid_data) < 2:
            return {
                'effect_size': np.nan,
                'interpretation': 'Insufficient data'
            }
        
        correlation = valid_data['x'].corr(valid_data['y'])
        abs_corr = abs(correlation)
        
        # Cohen's conventions for correlation effect sizes
        if abs_corr < 0.1:
            interpretation = 'Negligible'
        elif abs_corr < 0.3:
            interpretation = 'Small'
        elif abs_corr < 0.5:
            interpretation = 'Medium'
        else:
            interpretation = 'Large'
        
        return {
            'effect_size': correlation,
            'absolute_effect_size': abs_corr,
            'interpretation': interpretation
        }
    
    def perform_t_test(self, group1, group2, equal_var=True):
        """
        Perform independent t-test between two groups.
        
        Args:
            group1: First group data
            group2: Second group data
            equal_var: Assume equal variances (default True)
            
        Returns:
            Dictionary with t-test results
        """
        # Remove NaN values
        group1_clean = pd.Series(group1).dropna()
        group2_clean = pd.Series(group2).dropna()
        
        if len(group1_clean) < 2 or len(group2_clean) < 2:
            return {
                'statistic': np.nan,
                'p_value': np.nan,
                'is_significant': False,
                'error': 'Insufficient data in one or both groups'
            }
        
        # Perform t-test
        statistic, p_value = stats.ttest_ind(group1_clean, group2_clean, equal_var=equal_var)
        
        return {
            'statistic': statistic,
            'p_value': p_value,
            'is_significant': p_value < 0.05,
            'group1_mean': group1_clean.mean(),
            'group2_mean': group2_clean.mean(),
            'group1_size': len(group1_clean),
            'group2_size': len(group2_clean),
            'equal_var_assumed': equal_var
        }
    
    def calculate_confidence_interval_mean(self, data, confidence_level=0.95):
        """
        Calculate confidence interval for the mean.
        
        Args:
            data: Data series
            confidence_level: Confidence level (default 0.95)
            
        Returns:
            Dictionary with confidence interval information
        """
        clean_data = pd.Series(data).dropna()
        
        if len(clean_data) < 2:
            return {
                'mean': np.nan,
                'confidence_interval': (np.nan, np.nan),
                'margin_of_error': np.nan,
                'sample_size': len(clean_data)
            }
        
        mean = clean_data.mean()
        std_err = stats.sem(clean_data)  # Standard error of the mean
        
        # Calculate confidence interval
        alpha = 1 - confidence_level
        df = len(clean_data) - 1
        t_critical = stats.t.ppf(1 - alpha/2, df)
        
        margin_of_error = t_critical * std_err
        ci_lower = mean - margin_of_error
        ci_upper = mean + margin_of_error
        
        return {
            'mean': mean,
            'confidence_interval': (ci_lower, ci_upper),
            'margin_of_error': margin_of_error,
            'sample_size': len(clean_data),
            'confidence_level': confidence_level
        }
    
    def format_significance_display(self, correlation_result):
        """
        Format significance results for display.
        
        Args:
            correlation_result: Result from calculate_correlation_significance
            
        Returns:
            Formatted string for display
        """
        if 'error' in correlation_result:
            return correlation_result['error']
        
        corr = correlation_result['correlation']
        p_val = correlation_result['p_value']
        ci = correlation_result['confidence_interval']
        n = correlation_result['sample_size']
        
        # Get significance badge
        badge_info = self.get_significance_badge(p_val)
        
        # Format the display string
        display_parts = [
            "r = {:.3f}".format(corr),
            "p = {:.3f}".format(p_val),
            "95% CI: [{:.3f}, {:.3f}]".format(ci[0], ci[1]),
            "n = {}".format(n),
            badge_info['description']
        ]
        
        return " | ".join(display_parts)
    
    def create_significance_summary(self, correlations_dict):
        """
        Create a summary of multiple correlation significance tests.
        
        Args:
            correlations_dict: Dictionary of correlation results
            
        Returns:
            DataFrame with significance summary
        """
        summary_data = []
        
        for name, result in correlations_dict.items():
            if 'error' not in result:
                badge_info = self.get_significance_badge(result['p_value'])
                
                summary_data.append({
                    'Variable_Pair': name,
                    'Correlation': result['correlation'],
                    'P_Value': result['p_value'],
                    'Significance': badge_info['badge'],
                    'Effect_Size': result['strength'],
                    'Sample_Size': result['sample_size'],
                    'CI_Lower': result['confidence_interval'][0],
                    'CI_Upper': result['confidence_interval'][1]
                })
        
        return pd.DataFrame(summary_data)


def test_statistical_significance():
    """Test the statistical significance module."""
    print("Testing Statistical Significance Module")
    print("=" * 50)
    
    # Create sample data
    np.random.seed(42)
    n = 100
    
    # Strong positive correlation
    x1 = np.random.normal(0, 1, n)
    y1 = 0.8 * x1 + np.random.normal(0, 0.5, n)
    
    # Weak correlation
    x2 = np.random.normal(0, 1, n)
    y2 = 0.2 * x2 + np.random.normal(0, 1, n)
    
    # No correlation
    x3 = np.random.normal(0, 1, n)
    y3 = np.random.normal(0, 1, n)
    
    # Initialize analyzer
    analyzer = StatisticalSignificance()
    
    # Test correlations
    correlations = {
        'Strong_Positive': analyzer.calculate_correlation_significance(x1, y1),
        'Weak_Positive': analyzer.calculate_correlation_significance(x2, y2),
        'No_Correlation': analyzer.calculate_correlation_significance(x3, y3)
    }
    
    # Display results
    for name, result in correlations.items():
        print("\n{}:".format(name))
        print("  {}".format(analyzer.format_significance_display(result)))
        
        badge = analyzer.get_significance_badge(result['p_value'])
        print("  Badge: {} ({})".format(badge['badge'], badge['description']))
        
        effect = analyzer.calculate_effect_size(
            x1 if 'Strong' in name else (x2 if 'Weak' in name else x3),
            y1 if 'Strong' in name else (y2 if 'Weak' in name else y3)
        )
        print("  Effect size: {} ({})".format(
            effect['interpretation'], 
            "{:.3f}".format(effect['absolute_effect_size'])
        ))
    
    # Create summary
    summary = analyzer.create_significance_summary(correlations)
    print("\nSignificance Summary:")
    print(summary.round(3))
    
    print("\nStatistical significance module test completed successfully!")


if __name__ == "__main__":
    test_statistical_significance()