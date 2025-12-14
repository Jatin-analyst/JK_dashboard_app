# 🌬️ Air Quality vs Middle-Class Income Dashboard

A comprehensive Streamlit dashboard for exploratory analysis of relationships between air quality indicators, respiratory hospitalization burden, and economic stress indicators. This application uses real air quality data from Indian cities and generates correlated synthetic health and economic data to demonstrate meaningful relationships.

## ✨ Features

### 📊 Interactive Visualizations
- **Hero Chart**: Dual-axis visualization of AQI/PM2.5 vs Income Stress Index
- **Hospitalization Context**: Respiratory cases over time with high AQI period analysis
- **Environmental Context**: AQI correlations with temperature, wind speed, and seasonal patterns
- **Statistical Summary**: Correlation matrices and significance indicators

### 🎛️ Comprehensive Filtering
- **Geographic**: Location, region, urban/rural classification
- **Demographic**: Age groups, gender, income brackets
- **Environmental**: Seasons, weather conditions, pollution thresholds
- **Temporal**: Date ranges, time period grouping
- **Statistical**: Correlation strength, sample size, data completeness
- **Data Quality**: Outlier detection and exclusion options

### 📈 Advanced Analytics
- **Rolling Trend Analysis**: 7, 14, 30-day moving averages
- **Statistical Significance**: P-values, confidence intervals, effect sizes
- **Seasonal Pattern Detection**: Monthly and seasonal trend analysis
- **Data Quality Validation**: Completeness, outliers, duplicate detection

### 🔧 Performance Optimizations
- **Data Caching**: Efficient data loading with Streamlit caching
- **Memory Optimization**: Optimized data types for better performance
- **Progress Tracking**: Real-time loading progress indicators
- **Error Handling**: Comprehensive error handling with graceful fallbacks

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Required CSV data files (see Data Sources section)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd air-quality-income-dashboard
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ensure data files are present**
   The following files should be in the `data/` directory:
   - `city_day.csv` - Daily air quality data by city
   - `station_day.csv` - Daily air quality data by station
   - `stations.csv` - Station information

4. **Run the dashboard**
   ```bash
   streamlit run app.py
   ```

5. **Open in browser**
   Navigate to `http://localhost:8501`

## 🚀 Deployment Options

### 🐳 Docker Deployment (Recommended)

#### Using Docker Compose
```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

#### Using Docker directly
```bash
# Build image
docker build -t air-quality-dashboard .

# Run container
docker run -p 8501:8501 air-quality-dashboard
```

### ☁️ Cloud Deployment

#### Streamlit Cloud
1. Fork this repository to your GitHub account
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your GitHub repository
4. Deploy with one click
5. Add any secrets via the Streamlit Cloud interface

#### Other Cloud Platforms
- **Heroku**: Use the included `Dockerfile` for container deployment
- **Railway**: Connect GitHub repository directly
- **Render**: Deploy from GitHub with automatic builds
- **AWS/GCP/Azure**: Use container services (ECS, Cloud Run, Container Instances)

### 🔧 Production Configuration

#### Environment Variables
```bash
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_ENABLE_CORS=false
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

#### Production Requirements
Use `requirements-prod.txt` for production deployments:
```bash
pip install -r requirements-prod.txt
```

#### Streamlit Configuration
Customize `.streamlit/config.toml` for production settings:
- Theme colors and fonts
- Server configuration
- Security settings
- Performance optimizations

## 📁 Project Structure

```
air-quality-income-dashboard/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                      # Project documentation
├── data/                          # Data files
│   ├── city_day.csv              # Real air quality data
│   ├── station_day.csv           # Station-level data
│   └── stations.csv              # Station information
├── src/                          # Source code modules
│   ├── data/                     # Data processing
│   │   └── real_data_processor.py
│   ├── ui/                       # User interface components
│   │   ├── sidebar_filters.py
│   │   └── dashboard_layout.py
│   ├── filters/                  # Filtering logic
│   │   └── filter_manager.py
│   └── analysis/                 # Analysis modules
│       ├── trend_analysis.py
│       ├── statistical_significance.py
│       └── data_quality.py
└── .kiro/                        # Kiro specification files
    └── specs/air-quality-income-dashboard/
        ├── requirements.md
        ├── design.md
        └── tasks.md
```

## 📊 Data Sources

### Real Air Quality Data
- **Source**: Indian air quality monitoring stations
- **Coverage**: Major cities (Delhi, Mumbai, Chennai, Kolkata, Bangalore)
- **Metrics**: PM2.5, PM10, AQI, NO, NO2, CO, SO2, O3, and other pollutants
- **Time Period**: 2015-2024

### Synthetic Correlated Data
The application generates realistic synthetic data that correlates with real air quality measurements:

- **Health Data**: Respiratory cases and hospital days based on pollution levels
- **Economic Data**: Income stress calculations using wage and treatment cost estimates
- **Weather Data**: Temperature, wind speed, and seasonal patterns

### Income Stress Index Formula
```
Income Stress Index = (hospital_days × avg_daily_wage) + treatment_cost_est
```

## 🎯 Key Correlations Demonstrated

The dashboard reveals several meaningful relationships:

1. **AQI vs Income Stress**: Strong positive correlation (r ≈ 0.72)
2. **Seasonal Patterns**: Higher pollution in winter months
3. **Geographic Variations**: City-specific pollution and economic patterns
4. **Health Impact**: Increased respiratory cases during high AQI periods

## ⚠️ Important Disclaimers

**This dashboard is for reference and exploratory analysis only.**

- Makes no medical claims or predictions
- All correlations shown are exploratory in nature
- Should not be used for medical decision-making or policy implementation without proper scientific validation
- Synthetic health and economic data is generated for demonstration purposes

## 🔧 Technical Details

### Dependencies
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **SciPy**: Statistical functions
- **Plotly**: Interactive visualizations

### Performance Features
- **Caching**: Data loading cached for 1 hour
- **Memory Optimization**: Automatic data type optimization
- **Progress Tracking**: Real-time loading indicators
- **Error Handling**: Graceful fallbacks for all operations

### Statistical Methods
- **Correlation Analysis**: Pearson correlation with significance testing
- **Trend Analysis**: Rolling averages and seasonal decomposition
- **Quality Assessment**: Completeness, outlier detection, duplicate checking
- **Confidence Intervals**: 95% confidence intervals for all correlations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Air quality data sourced from Indian environmental monitoring networks
- Built with Streamlit and the Python data science ecosystem
- Developed using Kiro's specification-driven development methodology