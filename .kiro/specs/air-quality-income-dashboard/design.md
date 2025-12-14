# Air Quality vs Middle-Class Income Dashboard - Design Document

## Overview

The Air Quality vs Middle-Class Income Dashboard is a Streamlit-based web application that provides interactive exploratory analysis of relationships between air quality indicators, respiratory hospitalization burden, and economic stress indicators. The application emphasizes transparency, reproducibility, and appropriate use disclaimers while leveraging established Python libraries for all mathematical and statistical operations.

The dashboard follows a simple, defensible architecture that merges three CSV datasets (environmental, hospitalization, and income data) and provides interactive visualizations with demographic and geographic filtering capabilities. All correlations are exploratory in nature, with clear disclaimers about the limitations of the analysis.

## Architecture

The application follows a single-page Streamlit architecture with the following key components:

### Data Layer
- **CSV Data Sources**: Three primary datasets merged on date and location
  - `aqi_env.csv`: Environmental data including AQI, PM2.5, weather conditions
  - `hospital_cases.csv`: Respiratory hospitalization data with demographics
  - `income_proxy.csv`: Economic indicators for income stress calculation

### Processing Layer
- **Data Merger**: Pandas-based joining of datasets on date + location keys
- **Statistical Engine**: Scipy.stats for correlation calculations
- **Normalization Engine**: Numpy for min-max scaling operations
- **Trend Analysis**: Pandas rolling window calculations

### Presentation Layer
- **Streamlit Interface**: Single-page dashboard with comprehensive sidebar filters
- **Interactive Charts**: Dual-axis visualizations using Streamlit's native charting with zoom and pan capabilities
- **Advanced Filter Controls**: Multi-dimensional filtering including:
  - Geographic: Location, region, urban/rural classification
  - Demographic: Age group, gender, income bracket
  - Environmental: Season, weather conditions, pollution thresholds
  - Temporal: Date ranges, time of year, day of week
  - Statistical: Correlation strength, sample size, confidence intervals
  - Data Quality: Completeness thresholds, outlier detection

## Enhanced Filtering System

The dashboard provides comprehensive filtering capabilities to enable detailed exploratory analysis:

### Geographic Filters
- **Location Selection**: Multi-select dropdown for specific cities/areas
- **Regional Grouping**: Filter by broader geographic regions
- **Urban/Rural Classification**: Toggle between urban and rural areas
- **Distance-based Filtering**: Select areas within radius of a point

### Demographic and Socioeconomic Filters
- **Age Group Stratification**: Granular age brackets (0-18, 19-35, 36-50, 51-65, 65+)
- **Gender Analysis**: Male, Female, All genders options
- **Income Bracket Filtering**: Low, Middle, High income classifications
- **Employment Status**: If available in data, filter by employment categories

### Environmental and Temporal Filters
- **Seasonal Analysis**: Spring, Summer, Fall, Winter filtering
- **Weather Condition Filters**: Temperature ranges, wind speed thresholds
- **Pollution Level Thresholds**: Custom AQI and PM2.5 range selection
- **Date Range Selection**: Custom start and end date pickers
- **Time Period Grouping**: Daily, weekly, monthly aggregation options

### Statistical and Data Quality Filters
- **Correlation Strength Thresholds**: Filter results by minimum correlation strength
- **Sample Size Requirements**: Exclude analyses with insufficient data points
- **Data Completeness**: Filter out locations/periods with missing data above threshold
- **Outlier Detection**: Option to include/exclude statistical outliers
- **Confidence Interval Settings**: Adjustable confidence levels for statistical tests

### Advanced Analysis Parameters
- **Rolling Window Size**: Adjustable window for trend analysis (7, 14, 30, 90 days)
- **Normalization Method**: Choice between min-max, z-score, or robust scaling
- **Correlation Method**: Pearson, Spearman, or Kendall correlation options
- **Aggregation Level**: Individual records vs. aggregated summaries
- **Missing Data Handling**: Exclude, interpolate, or flag missing values

## Components and Interfaces

### Core Data Processing Module
```python
class DataProcessor:
    def load_and_merge_datasets() -> pd.DataFrame
    def calculate_income_stress_index() -> pd.Series
    def normalize_values() -> pd.DataFrame
    def calculate_correlations() -> dict
```

### Visualization Module
```python
class DashboardVisualizer:
    def render_hero_chart() -> None
    def render_hospitalization_context() -> None
    def render_environmental_context() -> None
    def render_statistical_summary() -> None
```

### Filter Management Module
```python
class FilterManager:
    def apply_location_filter() -> pd.DataFrame
    def apply_demographic_filter() -> pd.DataFrame
    def apply_environmental_filter() -> pd.DataFrame
    def apply_temporal_filter() -> pd.DataFrame
    def apply_threshold_filter() -> pd.DataFrame
    def apply_statistical_filter() -> pd.DataFrame
    def get_filtered_dataset() -> pd.DataFrame
    def get_available_filter_values() -> dict
```

## Data Models

### Environmental Data Model
```python
@dataclass
class EnvironmentalData:
    date: datetime
    location: str
    pm25: float
    pm10: float
    aqi: int
    temperature: float
    wind_speed: float
    sunlight: float
    season: str
```

### Hospitalization Data Model
```python
@dataclass
class HospitalizationData:
    date: datetime
    location: str
    age_group: str
    gender: str
    respiratory_cases: int
    hospital_days: int
```

### Income Proxy Data Model
```python
@dataclass
class IncomeProxyData:
    date: datetime
    location: str
    avg_daily_wage: float
    treatment_cost_est: float
```

### Merged Analysis Data Model
```python
@dataclass
class AnalysisData:
    date: datetime
    location: str
    region: str
    urban_rural: str
    pm25: float
    aqi: int
    respiratory_cases: int
    income_stress_index: float
    normalized_aqi: float
    normalized_stress: float
    correlation_coefficient: float
    confidence_interval: tuple
    sample_size: int
    data_completeness: float
    
@dataclass
class FilterParameters:
    locations: List[str]
    regions: List[str]
    age_groups: List[str]
    genders: List[str]
    seasons: List[str]
    date_range: tuple
    aqi_threshold_min: float
    aqi_threshold_max: float
    income_threshold_min: float
    income_threshold_max: float
    correlation_strength_min: float
    sample_size_min: int
    data_completeness_min: float
    exclude_outliers: bool
```
## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Pollutant Selection Updates Visualization
*For any* pollutant type selection (PM2.5 or AQI), changing the selection should update the hero chart to display data for the selected pollutant type
**Validates: Requirements 1.2**

### Property 2: Chart Data Normalization
*For any* dataset loaded into the dashboard, all chart values should fall within the normalized range [0, 1] when min-max scaling is applied
**Validates: Requirements 1.3**

### Property 3: Correlation Calculation Accuracy
*For any* two numeric datasets, the dashboard's correlation calculation should match the result from scipy.stats.pearsonr within floating-point precision
**Validates: Requirements 1.4**

### Property 4: Correlation Strength Classification
*For any* correlation coefficient value in the range [-1, 1], the dashboard should correctly classify it as Weak (|r| < 0.3), Moderate (0.3 ≤ |r| < 0.7), or Strong (|r| ≥ 0.7)
**Validates: Requirements 1.5**

### Property 5: High AQI Period Percentage Calculation
*For any* dataset with varying AQI levels, when high AQI periods are identified, the percentage increase calculation for respiratory cases should be mathematically accurate
**Validates: Requirements 2.2**

### Property 6: Demographic Stratification Accuracy
*For any* demographic filter combination (age group and gender), the filtered hospitalization data should contain only records matching the selected criteria
**Validates: Requirements 2.3**

### Property 7: Rolling Average Calculation
*For any* time series data, the rolling average calculations should match the results from pandas.DataFrame.rolling() for the same window size
**Validates: Requirements 2.4**

### Property 8: Data Merge Integrity
*For any* valid CSV datasets with date and location fields, the merge operation should preserve all matching records without data loss or corruption
**Validates: Requirements 2.5**

### Property 9: Filter Consistency Across Visualizations
*For any* filter selection, all dashboard visualizations should reflect the same filtered dataset consistently
**Validates: Requirements 3.2**

### Property 10: Location Filter Data Consistency
*For any* location filter applied, all merged datasets should maintain referential integrity with no orphaned or mismatched records
**Validates: Requirements 3.3**

### Property 11: Statistical Validity After Demographic Filtering
*For any* demographic subset, correlation calculations should remain mathematically valid and produce results within the valid correlation range [-1, 1]
**Validates: Requirements 3.4**

### Property 12: Environmental Filter Synchronization
*For any* environmental filter applied, both air quality and hospitalization context sections should update to reflect the same filtered dataset
**Validates: Requirements 3.5**

### Property 13: Environmental Correlation Accuracy
*For any* environmental dataset, correlation calculations between environmental variables should match scipy.stats results
**Validates: Requirements 4.3**

### Property 14: Seasonal Analysis Data Integration
*For any* dataset containing seasonal information, seasonal pattern analysis should correctly incorporate all season data without omission
**Validates: Requirements 4.4**

### Property 15: Statistical Significance Display
*For any* correlation calculation, statistical significance indicators should be accurately computed and displayed based on the correlation's p-value
**Validates: Requirements 4.5**

### Property 16: Income Stress Index Formula
*For any* input values for hospital_days, avg_daily_wage, and treatment_cost_est, the Income Stress Index should be calculated using the exact formula: stress = (hospital_days × avg_daily_wage) + treatment_cost_est
**Validates: Requirements 5.2**

### Property 17: Correlation Display with Labels
*For any* correlation value calculated, the dashboard should display both the numeric correlation coefficient and its corresponding strength label together
**Validates: Requirements 5.3**

### Property 18: Data Loading and Merging Success
*For any* valid CSV files matching the expected schema, the dashboard should successfully load and merge all three datasets (aqi_env.csv, hospital_cases.csv, income_proxy.csv) on date and location fields
**Validates: Requirements 6.1**

### Property 19: Reproducible Results
*For any* input dataset, running the same analysis multiple times should produce identical results across all calculations and visualizations
**Validates: Requirements 6.5**

## Error Handling

### Data Loading Errors
- **Missing Files**: Display clear error messages when CSV files are not found
- **Schema Validation**: Validate required columns exist in each dataset before processing
- **Data Type Errors**: Handle and report invalid data types in numeric columns
- **Merge Failures**: Detect and report when datasets cannot be merged due to missing keys

### Calculation Errors
- **Division by Zero**: Handle cases where wage or cost calculations involve zero values
- **Invalid Correlations**: Detect and handle cases where correlation cannot be computed (e.g., constant values)
- **Normalization Edge Cases**: Handle datasets with identical min/max values during normalization
- **Empty Datasets**: Gracefully handle empty or filtered datasets that result in no data

### User Interface Errors
- **Filter Conflicts**: Prevent filter combinations that result in empty datasets
- **Chart Rendering**: Handle cases where insufficient data prevents chart generation
- **Memory Limits**: Implement safeguards for large datasets that might exceed memory limits
- **Browser Compatibility**: Ensure graceful degradation for unsupported browser features

## Testing Strategy

### Dual Testing Approach
The application will use both unit testing and property-based testing to ensure comprehensive coverage:

- **Unit Tests**: Verify specific examples, edge cases, and integration points between components
- **Property-Based Tests**: Verify universal properties hold across all valid inputs using generated test data

### Property-Based Testing Framework
- **Library**: Hypothesis for Python will be used for property-based testing
- **Test Configuration**: Each property-based test will run a minimum of 100 iterations with random data generation
- **Property Tagging**: Each property-based test will include a comment explicitly referencing the corresponding correctness property from this design document using the format: '**Feature: air-quality-income-dashboard, Property {number}: {property_text}**'

### Unit Testing Coverage
- Data loading and CSV parsing functions
- Income Stress Index calculation with known input/output pairs
- Filter application logic with specific demographic combinations
- Chart rendering with predetermined datasets
- Error handling scenarios with invalid inputs

### Integration Testing
- End-to-end data flow from CSV loading through visualization rendering
- Filter interaction effects across multiple chart components
- Statistical calculation pipeline validation
- User interface responsiveness with various dataset sizes

### Test Data Strategy
- **Synthetic Datasets**: Generate controlled test data with known statistical properties
- **Edge Case Data**: Create datasets that test boundary conditions (empty, single-record, extreme values)
- **Real-world Samples**: Use anonymized sample data that reflects actual use patterns
- **Performance Data**: Test with large datasets to validate memory and processing efficiency