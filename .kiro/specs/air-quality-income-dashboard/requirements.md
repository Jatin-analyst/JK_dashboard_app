# Requirements Document

## Introduction

The Air Quality vs Middle-Class Income Dashboard is a Streamlit-based web application that provides exploratory analysis and visualization of the relationships between air quality indicators (AQI/PM2.5), respiratory hospitalization burden, and middle-class income stress. The dashboard enables users to interactively explore correlations and stratifications across these health, environmental, and economic dimensions while maintaining transparency about data limitations and avoiding predictive medical claims.

## Glossary

- **Dashboard**: The Streamlit web application interface
- **AQI**: Air Quality Index, a standardized measure of air pollution levels
- **PM2.5**: Particulate matter with diameter less than 2.5 micrometers
- **Income Stress Index**: A derived proxy metric calculated from hospitalization costs and daily wage loss
- **Respiratory Hospitalization Load**: The burden of respiratory-related hospital cases in a given area
- **Correlation Metric**: Statistical measure of relationship strength between variables using Pearson correlation
- **Stratification**: Segmentation of data by demographic or environmental factors

## Requirements

### Requirement 1

**User Story:** As a public health researcher, I want to visualize the relationship between air quality and income stress, so that I can explore potential correlations for further investigation.

#### Acceptance Criteria

1. WHEN a user accesses the dashboard THEN the Dashboard SHALL display an interactive dual-axis chart showing AQI/PM2.5 versus Income Stress Index
2. WHEN a user selects different pollutant types THEN the Dashboard SHALL update the visualization to reflect the selected pollutant data
3. WHEN chart data is displayed THEN the Dashboard SHALL show normalized values using min-max scaling
4. WHEN correlation analysis is performed THEN the Dashboard SHALL calculate and display Pearson correlation coefficients
5. WHEN correlation values are shown THEN the Dashboard SHALL label them as Weak, Moderate, or Strong based on statistical thresholds

### Requirement 2

**User Story:** As a healthcare analyst, I want to view hospitalization context alongside air quality data, so that I can understand respiratory health impacts during different pollution periods.

#### Acceptance Criteria

1. WHEN hospitalization data is displayed THEN the Dashboard SHALL show respiratory cases over time in a dedicated section
2. WHEN high AQI periods occur THEN the Dashboard SHALL calculate and display percentage increases in respiratory cases
3. WHEN users filter by demographics THEN the Dashboard SHALL stratify hospitalization data by age group and gender
4. WHEN rolling trends are calculated THEN the Dashboard SHALL use pandas rolling averages for temporal analysis
5. WHEN hospitalization metrics are computed THEN the Dashboard SHALL merge data on date and location fields

### Requirement 3

**User Story:** As a policy maker, I want to filter data by location, demographics, and environmental factors, so that I can focus analysis on specific populations or regions of interest.

#### Acceptance Criteria

1. WHEN a user accesses filter controls THEN the Dashboard SHALL provide sidebar filters for location, pollutant type, age group, gender, and season
2. WHEN filters are applied THEN the Dashboard SHALL update all visualizations to reflect the filtered dataset
3. WHEN location filtering occurs THEN the Dashboard SHALL maintain data consistency across all merged datasets
4. WHEN demographic stratification is selected THEN the Dashboard SHALL preserve statistical validity of correlation calculations
5. WHEN environmental filters are used THEN the Dashboard SHALL update both air quality and hospitalization context sections

### Requirement 4

**User Story:** As a data analyst, I want to see environmental context factors, so that I can understand how weather conditions relate to air quality patterns.

#### Acceptance Criteria

1. WHEN environmental context is displayed THEN the Dashboard SHALL show AQI versus temperature relationships
2. WHEN wind speed analysis is shown THEN the Dashboard SHALL visualize AQI versus wind speed correlations
3. WHEN environmental data is processed THEN the Dashboard SHALL use scipy.stats for correlation calculations
4. WHEN seasonal patterns are analyzed THEN the Dashboard SHALL incorporate season data from the environmental dataset
5. WHEN environmental correlations are computed THEN the Dashboard SHALL display statistical significance indicators

### Requirement 6

**User Story:** As a system administrator, I want the application to handle data processing reliably, so that users receive consistent and reproducible results.

#### Acceptance Criteria

1. WHEN data files are loaded THEN the Dashboard SHALL successfully merge aqi_env.csv, hospital_cases.csv, and income_proxy.csv on date and location fields
2. WHEN normalization is applied THEN the Dashboard SHALL use numpy for min-max scaling operations
3. WHEN correlation analysis runs THEN the Dashboard SHALL use scipy.stats.pearsonr for statistical calculations
4. WHEN rolling averages are computed THEN the Dashboard SHALL use pandas.DataFrame.rolling() methods
5. WHEN the application processes data THEN the Dashboard SHALL produce reproducible results across multiple runs
** this is my app structure **