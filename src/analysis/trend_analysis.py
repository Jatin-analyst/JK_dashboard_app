"""
Trend analysis module for rolling averages and temporal patterns.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class TrendAnalyzer:
    """
    Handles rolling trend analysis and temporal pattern detection.
    """
    
    def __init__(self):
        """Initialize the trend analyzer."""
        self.data = None
    
    def set_data(self, data):
        """Set the data for analysis."""
        self.data = data.copy()
        # Ensure date column is datetime
        if 'date' in self.data.columns:
            self.data['date'] = pd.to_datetime(self.data['date'])
            self.data = self.data.sort_values('date')
        return self
    
    def calculate_rolling_averages(self, column, window_sizes=[7, 14, 30]):
        """
        Calculate rolling averages for a given column.
        
        Args:
            column: Column name to calculate rolling averages for
            window_sizes: List of window sizes in days
            
        Returns:
            DataFrame with rolling averages added
        """
        if self.data is None or column not in self.data.columns:
            return None
        
        result_data = self.data.copy()
        
        for window in window_sizes:
            col_name = "{}_rolling_{}d".format(column, window)
            result_data[col_name] = result_data[column].rolling(
                window=window, min_periods=1
            ).mean()
        
        return result_data
    
    def create_rolling_trend_chart(self, column, location=None, window_sizes=[7, 14, 30]):
        """
        Create a chart showing rolling trends for a specific column.
        
        Args:
            column: Column to analyze
            location: Specific location to filter (optional)
            window_sizes: Rolling window sizes to display
            
        Returns:
            Plotly figure
        """
        if self.data is None:
            return None
        
        # Filter by location if specified
        plot_data = self.data.copy()
        if location and 'location' in plot_data.columns:
            plot_data = plot_data[plot_data['location'] == location]
        
        if len(plot_data) == 0:
            return None
        
        # Calculate rolling averages
        plot_data = self.calculate_rolling_averages(column, window_sizes)
        
        # Create figure
        fig = go.Figure()
        
        # Add original data
        fig.add_trace(go.Scatter(
            x=plot_data['date'],
            y=plot_data[column],
            mode='markers',
            name='Daily Values',
            marker=dict(size=4, opacity=0.5),
            line=dict(color='lightgray')
        ))
        
        # Add rolling averages
        colors = ['blue', 'red', 'green', 'orange', 'purple']
        for i, window in enumerate(window_sizes):
            col_name = "{}_rolling_{}d".format(column, window)
            if col_name in plot_data.columns:
                fig.add_trace(go.Scatter(
                    x=plot_data['date'],
                    y=plot_data[col_name],
                    mode='lines',
                    name='{}-day Average'.format(window),
                    line=dict(color=colors[i % len(colors)], width=2)
                ))
        
        # Update layout
        title = "Rolling Trends: {}".format(column.upper())
        if location:
            title += " ({})".format(location)
        
        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title=column.upper(),
            hovermode='x unified',
            height=400
        )
        
        return fig
    
    def detect_seasonal_patterns(self, column):
        """
        Detect seasonal patterns in the data.
        
        Args:
            column: Column to analyze for seasonal patterns
            
        Returns:
            Dictionary with seasonal statistics
        """
        if self.data is None or column not in self.data.columns:
            return {}
        
        # Add month and season columns
        analysis_data = self.data.copy()
        analysis_data['month'] = analysis_data['date'].dt.month
        
        def get_season(month):
            if month in [12, 1, 2]:
                return 'Winter'
            elif month in [3, 4, 5]:
                return 'Spring'
            elif month in [6, 7, 8]:
                return 'Summer'
            else:
                return 'Fall'
        
        analysis_data['season'] = analysis_data['month'].apply(get_season)
        
        # Calculate seasonal statistics
        seasonal_stats = analysis_data.groupby('season')[column].agg([
            'mean', 'std', 'min', 'max', 'count'
        ]).round(2)
        
        monthly_stats = analysis_data.groupby('month')[column].agg([
            'mean', 'std', 'count'
        ]).round(2)
        
        return {
            'seasonal': seasonal_stats.to_dict(),
            'monthly': monthly_stats.to_dict(),
            'overall_trend': self._calculate_overall_trend(analysis_data, column)
        }
    
    def _calculate_overall_trend(self, data, column):
        """Calculate overall trend direction."""
        if len(data) < 2:
            return 'insufficient_data'
        
        # Simple linear trend
        x = np.arange(len(data))
        y = data[column].values
        
        # Remove NaN values
        valid_mask = ~np.isnan(y)
        if np.sum(valid_mask) < 2:
            return 'insufficient_data'
        
        x_valid = x[valid_mask]
        y_valid = y[valid_mask]
        
        # Calculate slope
        slope = np.polyfit(x_valid, y_valid, 1)[0]
        
        if slope > 0.1:
            return 'increasing'
        elif slope < -0.1:
            return 'decreasing'
        else:
            return 'stable'
    
    def create_seasonal_comparison_chart(self, column):
        """
        Create a chart comparing seasonal patterns.
        
        Args:
            column: Column to analyze
            
        Returns:
            Plotly figure
        """
        if self.data is None:
            return None
        
        analysis_data = self.data.copy()
        analysis_data['month'] = analysis_data['date'].dt.month
        
        def get_season(month):
            if month in [12, 1, 2]:
                return 'Winter'
            elif month in [3, 4, 5]:
                return 'Spring'
            elif month in [6, 7, 8]:
                return 'Summer'
            else:
                return 'Fall'
        
        analysis_data['season'] = analysis_data['month'].apply(get_season)
        
        # Create box plot
        fig = px.box(
            analysis_data,
            x='season',
            y=column,
            title='Seasonal Distribution of {}'.format(column.upper()),
            category_orders={'season': ['Spring', 'Summer', 'Fall', 'Winter']}
        )
        
        fig.update_layout(height=400)
        return fig
    
    def create_monthly_trend_chart(self, column):
        """
        Create a chart showing monthly trends.
        
        Args:
            column: Column to analyze
            
        Returns:
            Plotly figure
        """
        if self.data is None:
            return None
        
        analysis_data = self.data.copy()
        analysis_data['month'] = analysis_data['date'].dt.month
        
        monthly_avg = analysis_data.groupby('month')[column].mean().reset_index()
        
        fig = px.line(
            monthly_avg,
            x='month',
            y=column,
            title='Monthly Average {}'.format(column.upper()),
            markers=True
        )
        
        fig.update_xaxes(
            tickmode='array',
            tickvals=list(range(1, 13)),
            ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        )
        
        fig.update_layout(height=400)
        return fig
    
    def get_trend_summary(self, column):
        """
        Get a comprehensive trend summary for a column.
        
        Args:
            column: Column to analyze
            
        Returns:
            Dictionary with trend summary
        """
        if self.data is None or column not in self.data.columns:
            return {}
        
        # Calculate rolling averages
        trend_data = self.calculate_rolling_averages(column, [7, 30])
        
        # Get seasonal patterns
        seasonal_info = self.detect_seasonal_patterns(column)
        
        # Calculate recent vs historical comparison
        if len(trend_data) > 60:  # At least 2 months of data
            recent_data = trend_data.tail(30)[column].mean()
            historical_data = trend_data.head(-30)[column].mean()
            change_pct = ((recent_data - historical_data) / historical_data) * 100
        else:
            recent_data = trend_data[column].mean()
            historical_data = recent_data
            change_pct = 0
        
        return {
            'current_7d_avg': trend_data["{}_rolling_7d".format(column)].iloc[-1] if len(trend_data) > 0 else None,
            'current_30d_avg': trend_data["{}_rolling_30d".format(column)].iloc[-1] if len(trend_data) > 0 else None,
            'overall_trend': seasonal_info.get('overall_trend', 'unknown'),
            'recent_vs_historical_change_pct': change_pct,
            'seasonal_patterns': seasonal_info.get('seasonal', {}),
            'data_points': len(trend_data),
            'date_range': (
                trend_data['date'].min().strftime('%Y-%m-%d'),
                trend_data['date'].max().strftime('%Y-%m-%d')
            ) if len(trend_data) > 0 else None
        }


def create_trend_analyzer(data):
    """
    Convenience function to create a trend analyzer.
    
    Args:
        data: DataFrame to analyze
        
    Returns:
        TrendAnalyzer instance
    """
    analyzer = TrendAnalyzer()
    analyzer.set_data(data)
    return analyzer


if __name__ == "__main__":
    # Test the trend analyzer
    import pandas as pd
    import numpy as np
    
    # Create sample data
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', periods=365, freq='D')
    
    # Create seasonal pattern
    seasonal_pattern = np.sin(2 * np.pi * np.arange(365) / 365) * 20
    trend = np.linspace(0, 10, 365)  # Slight upward trend
    noise = np.random.normal(0, 5, 365)
    
    sample_data = pd.DataFrame({
        'date': dates,
        'aqi': 100 + seasonal_pattern + trend + noise,
        'location': 'Test_City'
    })
    
    # Test trend analyzer
    analyzer = create_trend_analyzer(sample_data)
    
    # Test rolling averages
    rolling_data = analyzer.calculate_rolling_averages('aqi', [7, 14, 30])
    print("Rolling averages calculated for {} records".format(len(rolling_data)))
    
    # Test trend summary
    summary = analyzer.get_trend_summary('aqi')
    print("Trend Summary:")
    print("  7-day average: {:.1f}".format(summary['current_7d_avg']))
    print("  30-day average: {:.1f}".format(summary['current_30d_avg']))
    print("  Overall trend: {}".format(summary['overall_trend']))
    print("  Recent change: {:.1f}%".format(summary['recent_vs_historical_change_pct']))
    
    print("Trend analysis module test completed successfully!")