"""
Main dashboard layout structure for the Air Quality vs Income Dashboard.

This module creates the main dashboard layout with sections for hero chart,
hospitalization context, environmental context, statistical summary, and disclaimers.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
import hashlib
from functools import lru_cache

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
        self._chart_cache = {}
    
    def _generate_data_hash(self, data, additional_params=None):
        """
        Generate a stable hash for data and parameters to use as cache key.
        
        Args:
            data: DataFrame to hash
            additional_params: Additional parameters to include in hash
            
        Returns:
            String hash for caching
        """
        if data is None or len(data) == 0:
            return "empty_data"
        
        # Create hash from data shape, column names, and sample values
        hash_components = [
            str(data.shape),
            str(sorted(data.columns.tolist())),
            str(data.iloc[0].to_dict()) if len(data) > 0 else "no_data"
        ]
        
        if additional_params:
            hash_components.append(str(additional_params))
        
        hash_string = "|".join(hash_components)
        return hashlib.md5(hash_string.encode()).hexdigest()[:12]
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def _calculate_correlation(_self, data_hash, x_data, y_data, data_length):
        """
        Cached correlation calculation.
        
        Args:
            data_hash: Hash of the data for cache invalidation
            x_data: X variable data (as list for hashing)
            y_data: Y variable data (as list for hashing)
            data_length: Length of data for validation
            
        Returns:
            Correlation coefficient or None
        """
        try:
            x_series = pd.Series(x_data)
            y_series = pd.Series(y_data)
            
            if len(x_series) > 1 and len(y_series) > 1:
                correlation = x_series.corr(y_series)
                if not pd.isna(correlation) and np.isfinite(correlation):
                    return correlation
        except Exception:
            pass
        return None
    
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
        # Custom CSS for colorful metric cards inspired by the dashboard image
        st.markdown("""
        <style>
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin: 0.5rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .metric-card-orange {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
        .metric-card-green {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }
        .metric-card-purple {
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            color: #333;
        }
        .metric-card-blue {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .metric-number {
            font-size: 2rem;
            font-weight: bold;
            margin: 0;
        }
        .metric-label {
            font-size: 0.9rem;
            opacity: 0.9;
            margin: 0;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Header with greeting style
        col_title, col_actions = st.columns([3, 1])
        
        with col_title:
            st.markdown("# 🌬️ Air Quality Dashboard")
            st.markdown("**Exploring relationships between air quality, health, and economic indicators**")
        
        with col_actions:
            if st.button("🔄 Refresh Data", help="Reload the dashboard data"):
                st.rerun()
        
        # Colorful metric cards inspired by the dashboard image
        if self.data is not None and len(self.data) > 0:
            st.markdown("### 📊 Overview")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_records = len(self.data)
                st.markdown("""
                <div class="metric-card metric-card-blue">
                    <p class="metric-number">{:,}</p>
                    <p class="metric-label">Records</p>
                </div>
                """.format(total_records), unsafe_allow_html=True)
            
            with col2:
                unique_locations = self.data['location'].nunique() if 'location' in self.data.columns else 0
                st.markdown("""
                <div class="metric-card metric-card-orange">
                    <p class="metric-number">{}</p>
                    <p class="metric-label">Locations</p>
                </div>
                """.format(unique_locations), unsafe_allow_html=True)
            
            with col3:
                if 'aqi' in self.data.columns:
                    avg_aqi = self.data['aqi'].mean()
                    st.markdown("""
                    <div class="metric-card metric-card-green">
                        <p class="metric-number">{:.0f}</p>
                        <p class="metric-label">Avg AQI</p>
                    </div>
                    """.format(avg_aqi), unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="metric-card metric-card-green">
                        <p class="metric-number">N/A</p>
                        <p class="metric-label">Avg AQI</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col4:
                if 'respiratory_cases' in self.data.columns:
                    total_cases = self.data['respiratory_cases'].sum()
                    st.markdown("""
                    <div class="metric-card metric-card-purple">
                        <p class="metric-number">{:,}</p>
                        <p class="metric-label">Total Cases</p>
                    </div>
                    """.format(total_cases), unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="metric-card metric-card-purple">
                        <p class="metric-number">N/A</p>
                        <p class="metric-label">Total Cases</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Additional info row
            st.markdown("---")
            info_col1, info_col2, info_col3 = st.columns(3)
            
            with info_col1:
                if 'date' in self.data.columns:
                    date_range = (
                        self.data['date'].min().strftime('%Y-%m-%d'),
                        self.data['date'].max().strftime('%Y-%m-%d')
                    )
                    st.info("**Date Range:** {} to {}".format(date_range[0], date_range[1]))
                else:
                    st.info("📅 **Date Range:** Not available")
            
            with info_col2:
                if self.filter_summary:
                    retention_rate = self.filter_summary.get('retention_rate', 0)
                    active_filters = self.filter_summary.get('active_filters', 0)
                    st.info("**Filters:** {} active ({:.1%} data retained)".format(active_filters, retention_rate))
                else:
                    st.info("🎛️ **Filters:** None active (100% data retained)")
            
            with info_col3:
                data_quality = "Good" if len(self.data) > 100 else "Limited" if len(self.data) > 10 else "Poor"
                quality_color = "🟢" if data_quality == "Good" else "🟡" if data_quality == "Limited" else "🔴"
                st.info("**Data Quality:** {}".format(data_quality))
        
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
        
        # Initialize session state for pollutant selection
        if 'selected_pollutant' not in st.session_state:
            st.session_state.selected_pollutant = 'AQI'
        
        # Pollutant selection with improved layout
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col2:
            # Use radio buttons for better visual feedback
            pollutant_type = st.radio(
                "Select Pollutant Type:",
                options=['AQI', 'PM2.5'],
                index=0 if st.session_state.selected_pollutant == 'AQI' else 1,
                key="pollutant_selector_radio",
                help="Choose which air quality metric to display",
                horizontal=True
            )
            
            # Update session state when selection changes
            if pollutant_type != st.session_state.selected_pollutant:
                st.session_state.selected_pollutant = pollutant_type
                st.rerun()
        
        with col3:
            # Add refresh button for manual chart updates
            if st.button("🔄 Refresh Chart", key="refresh_hero_chart", help="Manually refresh the chart"):
                st.rerun()
        
        with col1:
            # Generate stable cache key for this chart
            chart_params = {
                'pollutant_type': pollutant_type,
                'data_shape': self.data.shape,
                'columns': sorted(self.data.columns.tolist())
            }
            data_hash = self._generate_data_hash(self.data, chart_params)
            
            # Check if we can use cached chart
            cache_key = "hero_chart_{}_{}" .format(pollutant_type, data_hash)
            
            # Show loading spinner while processing
            with st.spinner("Generating {} analysis...".format(pollutant_type)):
                # Calculate income stress index if not present (cached)
                if 'income_stress_index' not in self.data.columns:
                    if all(col in self.data.columns for col in ['hospital_days', 'avg_daily_wage', 'treatment_cost_est']):
                        income_stress = (self.data['hospital_days'] * self.data['avg_daily_wage']) + self.data['treatment_cost_est']
                    else:
                        st.error("Cannot calculate Income Stress Index. Missing required columns.")
                        return
                else:
                    income_stress = self.data['income_stress_index']
                
                # Select pollutant data based on current selection
                pollutant_data = self.data['aqi'] if pollutant_type == 'AQI' else self.data['pm25']
                
                # Optimize data for plotting (sample if too large)
                if len(self.data) > 1000:
                    sample_size = min(1000, len(self.data))
                    sample_indices = np.random.choice(len(self.data), sample_size, replace=False)
                    plot_data = self.data.iloc[sample_indices].copy()
                    plot_pollutant = pollutant_data.iloc[sample_indices]
                    plot_income_stress = income_stress.iloc[sample_indices]
                    st.info("Displaying sample of {:,} points from {:,} total records".format(sample_size, len(self.data)))
                else:
                    plot_data = self.data
                    plot_pollutant = pollutant_data
                    plot_income_stress = income_stress
                
                # Create dual-axis chart with improved styling and performance
                fig = make_subplots(
                    specs=[[{"secondary_y": True}]],
                    subplot_titles=["{} vs Income Stress Analysis".format(pollutant_type)]
                )
                
                # Add pollutant scatter plot with dynamic colors and optimized rendering
                scatter_color = 'Reds' if pollutant_type == 'AQI' else 'Blues'
                fig.add_trace(
                    go.Scattergl(  # Use WebGL for better performance
                        x=plot_data.index,
                        y=plot_pollutant,
                        mode='markers',
                        name="{} Level".format(pollutant_type),
                        marker=dict(
                            color=plot_pollutant,
                            colorscale=scatter_color,
                            size=8,
                            opacity=0.7,
                            line=dict(width=0.5, color='white'),
                            colorbar=dict(
                                title="{}".format(pollutant_type),
                                titleside="right"
                            )
                        ),
                        hovertemplate="<b>{}</b><br>".format(pollutant_type) +
                                    "Value: %{y}<br>" +
                                    "Index: %{x}<br>" +
                                    "<extra></extra>",
                        showlegend=True
                    ),
                    secondary_y=False,
                )
                
                # Add income stress line with improved styling
                fig.add_trace(
                    go.Scattergl(  # Use WebGL for better performance
                        x=plot_data.index,
                        y=plot_income_stress,
                        mode='lines+markers',
                        name='Income Stress Index',
                        line=dict(color='#2E86AB', width=2),
                        marker=dict(size=6, color='#2E86AB', line=dict(width=1, color='white')),
                        hovertemplate="<b>Income Stress</b><br>" +
                                    "Value: %{y:.0f}<br>" +
                                    "Index: %{x}<br>" +
                                    "<extra></extra>",
                        showlegend=True
                    ),
                    secondary_y=True,
                )
                
                # Update layout with improved styling and performance optimizations
                fig.update_xaxes(
                    title_text="Data Points",
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='rgba(128,128,128,0.2)'
                )
                fig.update_yaxes(
                    title_text="{} Level".format(pollutant_type),
                    secondary_y=False,
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='rgba(128,128,128,0.2)'
                )
                fig.update_yaxes(
                    title_text="Income Stress Index",
                    secondary_y=True,
                    showgrid=False
                )
                
                fig.update_layout(
                    title=dict(
                        text="{} vs Income Stress Relationship".format(pollutant_type),
                        x=0.5,
                        font=dict(size=16)
                    ),
                    hovermode='closest',
                    height=500,
                    showlegend=True,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=11),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ),
                    # Performance optimizations
                    dragmode='pan',
                    selectdirection='diagonal'
                )
                
                # Render chart with optimized key
                st.plotly_chart(fig, use_container_width=True, key=cache_key, config={
                    'displayModeBar': True,
                    'displaylogo': False,
                    'modeBarButtonsToRemove': ['lasso2d', 'select2d']
                })
                
                # Calculate and display correlation with caching
                if len(plot_pollutant) > 1 and len(plot_income_stress) > 1:
                    try:
                        # Use cached correlation calculation
                        correlation = self._calculate_correlation(
                            data_hash,
                            plot_pollutant.tolist(),
                            plot_income_stress.tolist(),
                            len(plot_pollutant)
                        )
                        
                        if correlation is not None:
                            # Classify correlation strength
                            abs_corr = abs(correlation)
                            if abs_corr < 0.3:
                                strength = 'Weak'
                                color = '#3498db'
                                emoji = '🔵'
                            elif abs_corr < 0.7:
                                strength = 'Moderate'
                                color = '#f39c12'
                                emoji = '🟡'
                            else:
                                strength = 'Strong'
                                color = '#e74c3c'
                                emoji = '🔴'
                            
                            # Enhanced correlation display with sample size info
                            st.markdown("""
                            <div style="padding: 15px; border-left: 4px solid {}; background-color: #f8f9fa; border-radius: 8px; margin: 10px 0;">
                                <h4 style="color: {}; margin: 0 0 8px 0;">{} Correlation Analysis</h4>
                                <p style="margin: 0 0 5px 0; font-size: 1.1em;"><strong>{} vs Income Stress:</strong> {:.3f}</p>
                                <p style="margin: 0 0 5px 0; color: {}; font-weight: bold;">Strength: {}</p>
                                <small style="color: #666;">Based on {:,} data points</small>
                            </div>
                            """.format(color, color, emoji, pollutant_type, correlation, color, strength, len(plot_pollutant)), unsafe_allow_html=True)
                        else:
                            st.info("⚠️ Correlation could not be calculated (insufficient data variation)")
                    except Exception as e:
                        st.warning("Could not calculate correlation: {}".format(str(e)))
                else:
                    st.info("⚠️ Insufficient data points for correlation analysis")
    
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
        # Check for statsmodels availability for trendlines
        try:
            import statsmodels.api as sm
            trendline_available = True
        except ImportError:
            trendline_available = False
        st.subheader("🌡️ Environmental Context")
        
        if self.data is None or len(self.data) == 0:
            st.error("No data available for environmental analysis.")
            return
        
        # Check what environmental data is available
        env_columns = ['temperature', 'wind_speed', 'season', 'aqi', 'pm25']
        available_env_cols = [col for col in env_columns if col in self.data.columns]
        
        if len(available_env_cols) < 2:
            st.warning("Insufficient environmental data for analysis. Available columns: {}".format(available_env_cols))
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            # AQI vs Temperature with improved error handling
            if 'aqi' in self.data.columns and 'temperature' in self.data.columns:
                # Clean data for correlation - remove NaN and infinite values
                temp_data = self.data[['temperature', 'aqi']].copy()
                temp_data = temp_data.dropna()
                temp_data = temp_data[np.isfinite(temp_data['temperature']) & np.isfinite(temp_data['aqi'])]
                
                if len(temp_data) > 1:
                    fig = px.scatter(
                        temp_data,
                        x='temperature',
                        y='aqi',
                        title='🌡️ AQI vs Temperature',
                        labels={'temperature': 'Temperature (°C)', 'aqi': 'Air Quality Index'},
                        color='aqi',
                        color_continuous_scale='Reds',
                        trendline='ols' if trendline_available else None
                    )
                    fig.update_layout(
                        height=400,
                        showlegend=False,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Calculate correlation with robust error handling
                    try:
                        if len(temp_data) > 2 and temp_data['temperature'].std() > 0 and temp_data['aqi'].std() > 0:
                            temp_aqi_corr = temp_data['temperature'].corr(temp_data['aqi'])
                            if not pd.isna(temp_aqi_corr) and np.isfinite(temp_aqi_corr):
                                # Classify correlation strength
                                abs_corr = abs(temp_aqi_corr)
                                if abs_corr < 0.3:
                                    strength = 'Weak'
                                    color = '#3498db'
                                    emoji = '🔵'
                                elif abs_corr < 0.7:
                                    strength = 'Moderate'
                                    color = '#f39c12'
                                    emoji = '🟡'
                                else:
                                    strength = 'Strong'
                                    color = '#e74c3c'
                                    emoji = '🔴'
                                
                                st.markdown("""
                                <div style="padding: 12px; border-left: 4px solid {}; background-color: #f8f9fa; border-radius: 8px; margin: 10px 0;">
                                    <h5 style="color: {}; margin: 0 0 5px 0;">{} Temperature-AQI Correlation</h5>
                                    <p style="margin: 0; font-size: 1.1em;"><strong>Correlation:</strong> {:.3f}</p>
                                    <p style="margin: 0; color: {}; font-weight: bold;">Strength: {}</p>
                                    <small style="color: #666;">Based on {} data points</small>
                                </div>
                                """.format(color, color, emoji, temp_aqi_corr, color, strength, len(temp_data)), unsafe_allow_html=True)
                            else:
                                st.info("💡 Unable to calculate temperature-AQI correlation (insufficient variation)")
                        else:
                            st.info("💡 Insufficient data variation for correlation calculation")
                    except Exception as e:
                        st.warning("Correlation calculation error: {}".format(str(e)))
                else:
                    st.info("Insufficient data points for temperature-AQI analysis")
            else:
                # Alternative visualization if temperature not available
                if 'pm25' in self.data.columns and 'aqi' in self.data.columns:
                    clean_data = self.data[['pm25', 'aqi']].dropna()
                    if len(clean_data) > 1:
                        fig = px.scatter(
                            clean_data,
                            x='pm25',
                            y='aqi',
                            title='🌫️ PM2.5 vs AQI',
                            labels={'pm25': 'PM2.5 (μg/m³)', 'aqi': 'Air Quality Index'},
                            color='aqi',
                            color_continuous_scale='Reds',
                            trendline='ols' if trendline_available else None
                        )
                        fig.update_layout(height=400, showlegend=False)
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Temperature and PM2.5 data not available")
        
        with col2:
            # AQI vs Wind Speed with improved error handling
            if 'aqi' in self.data.columns and 'wind_speed' in self.data.columns:
                wind_data = self.data[['wind_speed', 'aqi']].copy()
                wind_data = wind_data.dropna()
                wind_data = wind_data[np.isfinite(wind_data['wind_speed']) & np.isfinite(wind_data['aqi'])]
                
                if len(wind_data) > 1:
                    fig = px.scatter(
                        wind_data,
                        x='wind_speed',
                        y='aqi',
                        title='💨 AQI vs Wind Speed',
                        labels={'wind_speed': 'Wind Speed (m/s)', 'aqi': 'Air Quality Index'},
                        color='aqi',
                        color_continuous_scale='Blues',
                        trendline='ols' if trendline_available else None
                    )
                    fig.update_layout(
                        height=400,
                        showlegend=False,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Calculate correlation with robust error handling
                    try:
                        if len(wind_data) > 2 and wind_data['wind_speed'].std() > 0 and wind_data['aqi'].std() > 0:
                            wind_aqi_corr = wind_data['wind_speed'].corr(wind_data['aqi'])
                            if not pd.isna(wind_aqi_corr) and np.isfinite(wind_aqi_corr):
                                # Classify correlation strength
                                abs_corr = abs(wind_aqi_corr)
                                if abs_corr < 0.3:
                                    strength = 'Weak'
                                    color = '#3498db'
                                    emoji = '🔵'
                                elif abs_corr < 0.7:
                                    strength = 'Moderate'
                                    color = '#f39c12'
                                    emoji = '🟡'
                                else:
                                    strength = 'Strong'
                                    color = '#e74c3c'
                                    emoji = '🔴'
                                
                                st.markdown("""
                                <div style="padding: 12px; border-left: 4px solid {}; background-color: #f8f9fa; border-radius: 8px; margin: 10px 0;">
                                    <h5 style="color: {}; margin: 0 0 5px 0;">{} Wind Speed-AQI Correlation</h5>
                                    <p style="margin: 0; font-size: 1.1em;"><strong>Correlation:</strong> {:.3f}</p>
                                    <p style="margin: 0; color: {}; font-weight: bold;">Strength: {}</p>
                                    <small style="color: #666;">Based on {} data points</small>
                                </div>
                                """.format(color, color, emoji, wind_aqi_corr, color, strength, len(wind_data)), unsafe_allow_html=True)
                            else:
                                st.info("💡 Unable to calculate wind speed-AQI correlation (insufficient variation)")
                        else:
                            st.info("💡 Insufficient data variation for correlation calculation")
                    except Exception as e:
                        st.warning("Correlation calculation error: {}".format(str(e)))
                else:
                    st.info("Insufficient data points for wind speed-AQI analysis")
            else:
                # Alternative: Show AQI distribution
                if 'aqi' in self.data.columns:
                    fig = px.histogram(
                        self.data,
                        x='aqi',
                        title='📊 AQI Distribution',
                        labels={'aqi': 'Air Quality Index', 'count': 'Frequency'},
                        color_discrete_sequence=['#1f77b4']
                    )
                    fig.update_layout(height=400, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Wind speed and AQI data not available")
        
        # Seasonal analysis with improved error handling
        if 'season' in self.data.columns and len(self.data['season'].dropna()) > 0:
            st.subheader("🍂 Seasonal Patterns")
            
            seasonal_col1, seasonal_col2 = st.columns(2)
            
            with seasonal_col1:
                if 'aqi' in self.data.columns:
                    try:
                        seasonal_data = self.data[['season', 'aqi']].dropna()
                        if len(seasonal_data) > 0:
                            seasonal_aqi = seasonal_data.groupby('season')['aqi'].agg(['mean', 'count']).reset_index()
                            seasonal_aqi = seasonal_aqi[seasonal_aqi['count'] > 0]  # Only seasons with data
                            
                            if len(seasonal_aqi) > 0:
                                fig = px.bar(
                                    seasonal_aqi,
                                    x='season',
                                    y='mean',
                                    title='🌤️ Average AQI by Season',
                                    labels={'mean': 'Average AQI', 'season': 'Season'},
                                    color='mean',
                                    color_continuous_scale='Reds',
                                    text='mean'
                                )
                                fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
                                fig.update_layout(height=350, showlegend=False)
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("No seasonal AQI data available")
                        else:
                            st.info("No seasonal AQI data available")
                    except Exception as e:
                        st.info("Unable to generate seasonal AQI chart")
            
            with seasonal_col2:
                if 'respiratory_cases' in self.data.columns:
                    try:
                        seasonal_data = self.data[['season', 'respiratory_cases']].dropna()
                        if len(seasonal_data) > 0:
                            seasonal_cases = seasonal_data.groupby('season')['respiratory_cases'].agg(['mean', 'count']).reset_index()
                            seasonal_cases = seasonal_cases[seasonal_cases['count'] > 0]  # Only seasons with data
                            
                            if len(seasonal_cases) > 0:
                                fig = px.bar(
                                    seasonal_cases,
                                    x='season',
                                    y='mean',
                                    title='🏥 Average Respiratory Cases by Season',
                                    labels={'mean': 'Average Cases', 'season': 'Season'},
                                    color='mean',
                                    color_continuous_scale='Blues',
                                    text='mean'
                                )
                                fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
                                fig.update_layout(height=350, showlegend=False)
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("No seasonal respiratory cases data available")
                        else:
                            st.info("No seasonal respiratory cases data available")
                    except Exception as e:
                        st.info("Unable to generate seasonal respiratory cases chart")
        else:
            st.info("Seasonal data not available for pattern analysis")
    
    def render_statistical_summary_section(self):
        """Render the statistical summary section."""
        st.subheader("📈 Statistical Summary")
        
        if self.data is None or len(self.data) == 0:
            st.error("No data available for statistical analysis.")
            return
        
        # Key statistics with improved styling
        st.markdown("#### 📊 Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if 'aqi' in self.data.columns and not self.data['aqi'].isna().all():
                avg_aqi = self.data['aqi'].mean()
                max_aqi = self.data['aqi'].max()
                delta_aqi = avg_aqi - 100  # Compare to moderate AQI threshold
                st.metric(
                    "Average AQI",
                    "{:.1f}".format(avg_aqi),
                    delta="{:.1f} vs moderate".format(delta_aqi),
                    help="Mean Air Quality Index (100 = moderate threshold)"
                )
            else:
                st.metric("Average AQI", "N/A", help="AQI data not available")
        
        with col2:
            if 'pm25' in self.data.columns and not self.data['pm25'].isna().all():
                avg_pm25 = self.data['pm25'].mean()
                delta_pm25 = avg_pm25 - 35  # WHO guideline
                st.metric(
                    "Average PM2.5",
                    "{:.1f} μg/m³".format(avg_pm25),
                    delta="{:.1f} vs WHO".format(delta_pm25),
                    help="Mean PM2.5 concentration (35 μg/m³ = WHO guideline)"
                )
            else:
                st.metric("Average PM2.5", "N/A", help="PM2.5 data not available")
        
        with col3:
            if 'respiratory_cases' in self.data.columns and not self.data['respiratory_cases'].isna().all():
                total_cases = int(self.data['respiratory_cases'].sum())
                avg_cases = self.data['respiratory_cases'].mean()
                st.metric(
                    "Total Cases",
                    "{:,}".format(total_cases),
                    delta="Avg: {:.1f}".format(avg_cases),
                    help="Total respiratory cases in dataset"
                )
            else:
                st.metric("Total Cases", "N/A", help="Respiratory cases data not available")
        
        with col4:
            sample_size = len(self.data)
            original_size = self.filter_summary.get('original_records', sample_size) if self.filter_summary else sample_size
            retention = sample_size / original_size if original_size > 0 else 1
            st.metric(
                "Sample Size",
                "{:,}".format(sample_size),
                delta="{:.1%} retained".format(retention),
                help="Number of data points after filtering"
            )
        
        # Enhanced correlation analysis
        numeric_cols = self.data.select_dtypes(include=['float64', 'int64', 'float32', 'int32']).columns
        if len(numeric_cols) > 1:
            st.markdown("#### 🔗 Correlation Analysis")
            
            # Select key columns for correlation
            key_cols = []
            col_labels = {}
            for col, label in [('aqi', 'AQI'), ('pm25', 'PM2.5'), ('respiratory_cases', 'Respiratory Cases'), 
                              ('temperature', 'Temperature'), ('wind_speed', 'Wind Speed')]:
                if col in numeric_cols and not self.data[col].isna().all():
                    key_cols.append(col)
                    col_labels[col] = label
            
            if len(key_cols) > 1:
                # Calculate correlation matrix with clean data
                clean_data = self.data[key_cols].dropna()
                
                if len(clean_data) > 1:
                    corr_matrix = clean_data.corr()
                    
                    # Create correlation heatmap
                    fig = px.imshow(
                        corr_matrix,
                        text_auto='.3f',
                        aspect="auto",
                        title="🔗 Correlation Matrix of Key Variables",
                        color_continuous_scale='RdBu_r',
                        zmin=-1,
                        zmax=1,
                        labels=dict(x="Variables", y="Variables", color="Correlation")
                    )
                    
                    # Update layout for better appearance
                    fig.update_layout(
                        height=500,
                        font=dict(size=12),
                        title_x=0.5,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)'
                    )
                    
                    # Update axis labels
                    fig.update_xaxes(tickangle=45)
                    fig.update_yaxes(tickangle=0)
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show strongest correlations
                    st.markdown("#### 🎯 Strongest Correlations")
                    
                    # Find strongest correlations (excluding self-correlations)
                    correlations = []
                    for i in range(len(key_cols)):
                        for j in range(i+1, len(key_cols)):
                            corr_val = corr_matrix.iloc[i, j]
                            if not pd.isna(corr_val):
                                correlations.append({
                                    'var1': col_labels.get(key_cols[i], key_cols[i]),
                                    'var2': col_labels.get(key_cols[j], key_cols[j]),
                                    'correlation': corr_val,
                                    'abs_correlation': abs(corr_val)
                                })
                    
                    # Sort by absolute correlation and show top 3
                    correlations.sort(key=lambda x: x['abs_correlation'], reverse=True)
                    
                    corr_col1, corr_col2, corr_col3 = st.columns(3)
                    
                    for idx, corr in enumerate(correlations[:3]):
                        col = [corr_col1, corr_col2, corr_col3][idx]
                        
                        # Determine strength and color
                        abs_corr = corr['abs_correlation']
                        if abs_corr >= 0.7:
                            strength = "Strong"
                            color = "#e74c3c"
                        elif abs_corr >= 0.3:
                            strength = "Moderate"
                            color = "#f39c12"
                        else:
                            strength = "Weak"
                            color = "#3498db"
                        
                        with col:
                            st.markdown("""
                            <div style="padding: 15px; border: 2px solid {}; border-radius: 10px; text-align: center; background-color: #f8f9fa;">
                                <h4 style="color: {}; margin: 0;">{:.3f}</h4>
                                <p style="margin: 5px 0; font-weight: bold;">{} ↔ {}</p>
                                <p style="margin: 0; color: {}; font-size: 0.9em;">{} Correlation</p>
                            </div>
                            """.format(color, color, corr['correlation'], corr['var1'], corr['var2'], color, strength), unsafe_allow_html=True)
                else:
                    st.info("Insufficient clean data for correlation analysis")
            else:
                st.info("Need at least 2 numeric variables for correlation analysis")
        else:
            st.info("No numeric data available for correlation analysis")
    
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
        """Render the complete dashboard layout with performance monitoring."""
        import time
        start_time = time.time()
        
        # Header
        header_start = time.time()
        self.render_header()
        header_time = time.time() - header_start
        
        # Disclaimer
        self.render_disclaimer()
        
        # Main content sections
        if self.data is not None and len(self.data) > 0:
            # Performance monitoring for each section
            section_times = {}
            
            # Hero chart
            section_start = time.time()
            self.render_hero_chart_section()
            section_times['Hero Chart'] = time.time() - section_start
            st.markdown("---")
            
            # Hospitalization context
            section_start = time.time()
            self.render_hospitalization_context_section()
            section_times['Hospitalization'] = time.time() - section_start
            st.markdown("---")
            
            # Environmental context
            section_start = time.time()
            self.render_environmental_context_section()
            section_times['Environmental'] = time.time() - section_start
            st.markdown("---")
            
            # Statistical summary
            section_start = time.time()
            self.render_statistical_summary_section()
            section_times['Statistics'] = time.time() - section_start
            
            # Show performance info in debug mode
            total_time = time.time() - start_time
            if st.sidebar.checkbox("🔧 Show Performance Info", value=False, help="Display rendering performance metrics"):
                with st.expander("⚡ Performance Metrics", expanded=False):
                    perf_col1, perf_col2 = st.columns(2)
                    
                    with perf_col1:
                        st.metric("Total Render Time", "{:.2f}s".format(total_time))
                        st.metric("Header Time", "{:.2f}s".format(header_time))
                    
                    with perf_col2:
                        st.metric("Data Size", "{:,} rows".format(len(self.data)))
                        st.metric("Memory Usage", "{:.1f} MB".format(self.data.memory_usage(deep=True).sum() / 1024 / 1024))
                    
                    st.subheader("Section Render Times")
                    for section, render_time in section_times.items():
                        st.text("{}: {:.2f}s".format(section, render_time))
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