"""
Main dashboard layout structure for the Air Quality vs Income Dashboard.

This module creates the main dashboard layout with sections for hero chart,
hospitalization context, environmental context, statistical summary, and disclaimers.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


class DashboardLayout:
    """
    Creates and manages the main dashboard layout structure.
    """
    
    def __init__(self):
        """Initialize the dashboard layout."""
        self.data = None
        self.filter_summary = None
    
    def set_data(self, data, filter_summary=None):
        """
        Set the data for the dashboard.
        
        Args:
            data: Filtered DataFrame to display
            filter_summary: Summary of applied filters
        """
        self.data = data
        self.filter_summary = filter_summary
        return self
    
    def render_header(self):
        """Render the dashboard header with title and description."""
        st.title("🌬️ Air Quality vs Middle-Class Income Dashboard")
        
        # Subtitle with key metrics
        if self.data is not None and len(self.data) > 0:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Records", 
                    len(self.data),
                    help="Number of data points in current view"
                )
            
            with col2:
                unique_locations = self.data['location'].nunique() if 'location' in self.data.columns else 0
                st.metric(
                    "Locations", 
                    unique_locations,
                    help="Number of unique locations in dataset"
                )
            
            with col3:
                if 'date' in self.data.columns:
                    date_range = (
                        self.data['date'].min().strftime('%Y-%m-%d'),
                        self.data['date'].max().strftime('%Y-%m-%d')
                    )
                    st.metric(
                        "Date Range",
                        "{} to {}".format(*date_range),
                        help="Time period covered by current data"
                    )
                else:
                    st.metric("Date Range", "N/A")
            
            with col4:
                if self.filter_summary:
                    retention_rate = self.filter_summary.get('retention_rate', 0)
                    st.metric(
                        "Data Retention",
                        "{:.1%}".format(retention_rate),
                        help="Percentage of original data after filtering"
                    )
                else:
                    st.metric("Data Retention", "100%")
        
        st.markdown("---")
    
    def render_disclaimer(self):
        """Render the prominent disclaimer section."""
        st.warning("""
        **⚠️ IMPORTANT DISCLAIMER**: This dashboard is for reference and exploratory analysis only. 
        It makes no medical claims or predictions. All correlations shown are exploratory 
        in nature and should not be used for medical decision-making or policy implementation 
        without proper scientific validation.
        """)
    
    def render_hero_chart_section(self):
        """Render the hero chart section with AQI/PM2.5 vs Income Stress visualization."""
        st.subheader("📊 Primary Analysis: Air Quality vs Income Stress")
        
        if self.data is None or len(self.data) == 0:
            st.error("No data available for visualization. Please adjust your filters.")
            return
        
        # Check for required columns
        required_cols = ['aqi', 'pm25']
        missing_cols = [col for col in required_cols if col not in self.data.columns]
        
        if missing_cols:
            st.error("Missing required columns for hero chart: {}".format(missing_cols))
            return
        
        # Pollutant selection
        col1, col2 = st.columns([3, 1])
        
        with col2:
            pollutant_type = st.selectbox(
                "Select Pollutant",
                options=['AQI', 'PM2.5'],
                help="Choose which air quality metric to display"
            )
        
        with col1:
            # Calculate income stress index if not present
            if 'income_stress_index' not in self.data.columns:
                if all(col in self.data.columns for col in ['hospital_days', 'avg_daily_wage', 'treatment_cost_est']):
                    income_stress = (self.data['hospital_days'] * self.data['avg_daily_wage']) + self.data['treatment_cost_est']
                else:
                    st.error("Cannot calculate Income Stress Index. Missing required columns.")
                    return
            else:
                income_stress = self.data['income_stress_index']
            
            # Select pollutant data
            pollutant_data = self.data['aqi'] if pollutant_type == 'AQI' else self.data['pm25']
            
            # Create dual-axis chart
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Add pollutant scatter plot
            fig.add_trace(
                go.Scatter(
                    x=self.data.index,
                    y=pollutant_data,
                    mode='markers',
                    name=pollutant_type,
                    marker=dict(
                        color=pollutant_data,
                        colorscale='Reds',
                        size=8,
                        opacity=0.7
                    ),
                    hovertemplate="<b>%{fullData.name}</b><br>" +
                                "Value: %{y}<br>" +
                                "<extra></extra>"
                ),
                secondary_y=False,
            )
            
            # Add income stress line
            fig.add_trace(
                go.Scatter(
                    x=self.data.index,
                    y=income_stress,
                    mode='lines+markers',
                    name='Income Stress Index',
                    line=dict(color='blue', width=2),
                    marker=dict(size=6),
                    hovertemplate="<b>Income Stress</b><br>" +
                                "Value: %{y:.0f}<br>" +
                                "<extra></extra>"
                ),
                secondary_y=True,
            )
            
            # Update layout
            fig.update_xaxes(title_text="Data Points")
            fig.update_yaxes(title_text="{} Level".format(pollutant_type), secondary_y=False)
            fig.update_yaxes(title_text="Income Stress Index", secondary_y=True)
            
            fig.update_layout(
                title="Air Quality vs Income Stress Relationship",
                hovermode='x unified',
                height=500,
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display correlation
            if len(pollutant_data) > 1 and len(income_stress) > 1:
                correlation = pollutant_data.corr(income_stress)
                
                # Classify correlation strength
                abs_corr = abs(correlation)
                if abs_corr < 0.3:
                    strength = 'Weak'
                    color = 'blue'
                elif abs_corr < 0.7:
                    strength = 'Moderate'
                    color = 'orange'
                else:
                    strength = 'Strong'
                    color = 'red'
                
                st.info("**Correlation**: {:.3f} ({} relationship)".format(correlation, strength))
    
    def render_hospitalization_context_section(self):
        """Render the hospitalization context section."""
        st.subheader("🏥 Hospitalization Context")
        
        if self.data is None or len(self.data) == 0:
            st.error("No data available for hospitalization analysis.")
            return
        
        if 'respiratory_cases' not in self.data.columns:
            st.error("Respiratory cases data not available.")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Respiratory cases over time
            if 'date' in self.data.columns:
                fig = px.line(
                    self.data, 
                    x='date', 
                    y='respiratory_cases',
                    title='Respiratory Cases Over Time',
                    labels={'respiratory_cases': 'Number of Cases', 'date': 'Date'}
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                # Bar chart if no date column
                location_cases = self.data.groupby('location')['respiratory_cases'].sum().reset_index()
                fig = px.bar(
                    location_cases,
                    x='location',
                    y='respiratory_cases',
                    title='Respiratory Cases by Location'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # High AQI period analysis
            if 'aqi' in self.data.columns and len(self.data) > 0:
                aqi_threshold = st.slider(
                    "AQI Threshold for 'High' Classification",
                    min_value=int(self.data['aqi'].min()),
                    max_value=int(self.data['aqi'].max()),
                    value=100,
                    help="Define what constitutes 'high' AQI for analysis"
                )
                
                # Calculate percentage increase
                high_aqi = self.data[self.data['aqi'] >= aqi_threshold]
                normal_aqi = self.data[self.data['aqi'] < aqi_threshold]
                
                if len(high_aqi) > 0 and len(normal_aqi) > 0:
                    avg_high = high_aqi['respiratory_cases'].mean()
                    avg_normal = normal_aqi['respiratory_cases'].mean()
                    
                    if avg_normal > 0:
                        percentage_increase = ((avg_high - avg_normal) / avg_normal) * 100
                        
                        st.metric(
                            "Cases During High AQI",
                            "{:.1f}".format(avg_high),
                            delta="{:.1f}%".format(percentage_increase),
                            help="Average respiratory cases during high AQI periods"
                        )
                        
                        st.metric(
                            "Cases During Normal AQI",
                            "{:.1f}".format(avg_normal),
                            help="Average respiratory cases during normal AQI periods"
                        )
                        
                        st.metric(
                            "High AQI Days",
                            len(high_aqi),
                            help="Number of days with AQI >= {}".format(aqi_threshold)
                        )
                    else:
                        st.info("Insufficient data for percentage calculation")
                else:
                    st.info("No data available for the selected AQI threshold")
            else:
                st.info("AQI data not available for high period analysis")
        
        # Demographic stratification
        if 'age_group' in self.data.columns or 'gender' in self.data.columns:
            st.subheader("👥 Demographic Breakdown")
            
            demo_col1, demo_col2 = st.columns(2)
            
            with demo_col1:
                if 'age_group' in self.data.columns:
                    age_cases = self.data.groupby('age_group')['respiratory_cases'].sum().reset_index()
                    fig = px.pie(
                        age_cases,
                        values='respiratory_cases',
                        names='age_group',
                        title='Cases by Age Group'
                    )
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
            
            with demo_col2:
                if 'gender' in self.data.columns:
                    gender_cases = self.data.groupby('gender')['respiratory_cases'].sum().reset_index()
                    fig = px.pie(
                        gender_cases,
                        values='respiratory_cases',
                        names='gender',
                        title='Cases by Gender'
                    )
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
    
    def render_environmental_context_section(self):
        """Render the environmental context section."""
        st.subheader("🌡️ Environmental Context")
        
        if self.data is None or len(self.data) == 0:
            st.error("No data available for environmental analysis.")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            # AQI vs Temperature
            if 'aqi' in self.data.columns and 'temperature' in self.data.columns:
                fig = px.scatter(
                    self.data,
                    x='temperature',
                    y='aqi',
                    title='AQI vs Temperature',
                    labels={'temperature': 'Temperature (°C)', 'aqi': 'Air Quality Index'},
                    trendline='ols'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                # Calculate correlation
                temp_aqi_corr = self.data['temperature'].corr(self.data['aqi'])
                st.info("**Temperature-AQI Correlation**: {:.3f}".format(temp_aqi_corr))
            else:
                st.info("Temperature or AQI data not available")
        
        with col2:
            # AQI vs Wind Speed
            if 'aqi' in self.data.columns and 'wind_speed' in self.data.columns:
                fig = px.scatter(
                    self.data,
                    x='wind_speed',
                    y='aqi',
                    title='AQI vs Wind Speed',
                    labels={'wind_speed': 'Wind Speed (m/s)', 'aqi': 'Air Quality Index'},
                    trendline='ols'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                # Calculate correlation
                wind_aqi_corr = self.data['wind_speed'].corr(self.data['aqi'])
                st.info("**Wind Speed-AQI Correlation**: {:.3f}".format(wind_aqi_corr))
            else:
                st.info("Wind speed or AQI data not available")
        
        # Seasonal analysis
        if 'season' in self.data.columns:
            st.subheader("🍂 Seasonal Patterns")
            
            seasonal_col1, seasonal_col2 = st.columns(2)
            
            with seasonal_col1:
                if 'aqi' in self.data.columns:
                    seasonal_aqi = self.data.groupby('season')['aqi'].mean().reset_index()
                    fig = px.bar(
                        seasonal_aqi,
                        x='season',
                        y='aqi',
                        title='Average AQI by Season',
                        color='aqi',
                        color_continuous_scale='Reds'
                    )
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
            
            with seasonal_col2:
                if 'respiratory_cases' in self.data.columns:
                    seasonal_cases = self.data.groupby('season')['respiratory_cases'].mean().reset_index()
                    fig = px.bar(
                        seasonal_cases,
                        x='season',
                        y='respiratory_cases',
                        title='Average Respiratory Cases by Season',
                        color='respiratory_cases',
                        color_continuous_scale='Blues'
                    )
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
    
    def render_statistical_summary_section(self):
        """Render the statistical summary section."""
        st.subheader("📈 Statistical Summary")
        
        if self.data is None or len(self.data) == 0:
            st.error("No data available for statistical analysis.")
            return
        
        # Key statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if 'aqi' in self.data.columns:
                st.metric(
                    "Average AQI",
                    "{:.1f}".format(self.data['aqi'].mean()),
                    help="Mean Air Quality Index"
                )
        
        with col2:
            if 'pm25' in self.data.columns:
                st.metric(
                    "Average PM2.5",
                    "{:.1f} μg/m³".format(self.data['pm25'].mean()),
                    help="Mean PM2.5 concentration"
                )
        
        with col3:
            if 'respiratory_cases' in self.data.columns:
                st.metric(
                    "Total Cases",
                    "{:,}".format(int(self.data['respiratory_cases'].sum())),
                    help="Total respiratory cases"
                )
        
        with col4:
            st.metric(
                "Sample Size",
                "{:,}".format(len(self.data)),
                help="Number of data points"
            )
        
        # Correlation matrix
        numeric_cols = self.data.select_dtypes(include=['float64', 'int64']).columns
        if len(numeric_cols) > 1:
            st.subheader("🔗 Correlation Matrix")
            
            # Select key columns for correlation
            key_cols = []
            for col in ['aqi', 'pm25', 'respiratory_cases', 'temperature', 'wind_speed']:
                if col in numeric_cols:
                    key_cols.append(col)
            
            if len(key_cols) > 1:
                corr_matrix = self.data[key_cols].corr()
                
                fig = px.imshow(
                    corr_matrix,
                    text_auto=True,
                    aspect="auto",
                    title="Correlation Matrix of Key Variables",
                    color_continuous_scale='RdBu_r',
                    zmin=-1,
                    zmax=1
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
    
    def render_footer(self):
        """Render the footer with data sources and methodology."""
        st.markdown("---")
        st.subheader("📚 Data Sources & Methodology")
        
        st.markdown("""
        **Data Sources:**
        - Environmental data: AQI and PM2.5 measurements with weather conditions
        - Hospitalization data: Respiratory case counts with demographic information  
        - Income proxy: Economic stress indicators derived from wage and treatment cost estimates
        
        **Methodology:**
        - Income Stress Index Formula: `(hospital_days × avg_daily_wage) + treatment_cost_est`
        - All statistical calculations use established Python libraries (pandas, numpy, scipy)
        - Correlations calculated using Pearson correlation coefficient
        - Data normalization uses min-max scaling (0-1 range)
        
        **Correlation Strength Classification:**
        - Weak: |r| < 0.3
        - Moderate: 0.3 ≤ |r| < 0.7  
        - Strong: |r| ≥ 0.7
        """)
    
    def render_complete_dashboard(self):
        """Render the complete dashboard layout."""
        # Header
        self.render_header()
        
        # Disclaimer
        self.render_disclaimer()
        
        # Main content sections
        if self.data is not None and len(self.data) > 0:
            # Hero chart
            self.render_hero_chart_section()
            st.markdown("---")
            
            # Hospitalization context
            self.render_hospitalization_context_section()
            st.markdown("---")
            
            # Environmental context
            self.render_environmental_context_section()
            st.markdown("---")
            
            # Statistical summary
            self.render_statistical_summary_section()
        else:
            st.error("No data available. Please check your data source and filters.")
        
        # Footer
        self.render_footer()


def create_dashboard_layout(data, filter_summary=None):
    """
    Convenience function to create the complete dashboard layout.
    
    Args:
        data: DataFrame to display
        filter_summary: Optional filter summary information
        
    Returns:
        DashboardLayout instance
    """
    layout = DashboardLayout()
    layout.set_data(data, filter_summary)
    layout.render_complete_dashboard()
    return layout


if __name__ == "__main__":
    print("Dashboard layout module loaded successfully!")
    print("Use create_dashboard_layout(data) in your Streamlit app to render the complete dashboard.")