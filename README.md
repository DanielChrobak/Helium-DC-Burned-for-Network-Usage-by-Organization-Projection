# Daily DC Burned Forecasting System

A sophisticated time series forecasting dashboard for predicting Daily DC (Data Credits) burned by Organizational Unit Identifier (OUI) in the Helium network. This system implements advanced statistical methods including outlier detection, robust regression, seasonal decomposition, and autoregressive modeling to generate accurate multi-day projections.

## Project Overview

This forecasting system processes historical DC burned data from the Helium network and generates probabilistic projections using a comprehensive ensemble of time series techniques. The system is designed to handle real-world data challenges including outliers, seasonal patterns, and varying temporal contexts.

### Key Features

- **Advanced Outlier Detection**: Multiple methods (IQR, Modified Z-Score, Seasonal)
- **Robust Trend Analysis**: Huber regression resistant to anomalies
- **Comprehensive Seasonality**: Day-of-week, monthly, quarterly, and holiday effects
- **Context-Aware Modeling**: Separate models for weekdays, weekends, holidays
- **Autoregressive Components**: Automatic AR model selection using AIC
- **Bootstrap Uncertainty**: Probabilistic forecasts with realistic variation
- **Walk-Forward Validation**: Rigorous performance assessment
- **Interactive Visualization**: Real-time charts with Plotly.js

## System Architecture

```
Data Source (Dune) -> Flask Backend -> Interactive Dashboard
                        |   |   |
                        v   v   v
dune_query_result.json -> /data API -> JavaScript Algorithms
```

## Algorithm Deep Dive

### 1. Data Processing Pipeline

The forecasting algorithm follows a comprehensive multi-stage approach:

#### Stage 1: Outlier Detection & Data Cleaning
Multiple outlier detection methods for robust identification:
- IQR Method: Identifies values beyond Q1 - 1.5*IQR or Q3 + 1.5*IQR
- Modified Z-Score: Uses median and MAD for robust outlier detection
- Seasonal Outliers: Detects anomalies within seasonal patterns
- Winsorization: Caps extreme values rather than removing them

#### Stage 2: Trend Estimation
Robust regression resistant to outliers using Huber regression:
- Iteratively reweighted least squares with Huber loss function
- Provides full weight to small residuals, reduced weight for large ones
- More robust than ordinary least squares for data with outliers

#### Stage 3: Seasonal Decomposition
Comprehensive seasonal pattern extraction with components:
- **Day-of-Week Effects**: Different patterns for Monday through Sunday
- **Monthly Effects**: Seasonal variations across 12 months
- **Quarterly Effects**: Business cycle patterns (Q1, Q2, Q3, Q4)
- **Holiday Effects**: Special handling for major holidays
- **Calendar Effects**: Month-start and month-end patterns

#### Stage 4: Context-Aware Residual Modeling
Separate AR models for different temporal contexts:
- Automatic order selection using Akaike Information Criterion (AIC)
- Ljung-Box test for autocorrelation significance
- Context-specific models capture different temporal dependencies

#### Stage 5: Forecast Generation
Multi-component forecast combination:

```
forecast = trend + seasonal_effects + autoregressive_component + random_innovation
```

### 2. Bootstrap Sampling for Uncertainty

The system implements block bootstrap sampling to generate realistic forecast uncertainty by preserving short-term temporal dependencies through block sampling.

### 3. Walk-Forward Validation

Rigorous performance assessment using time series cross-validation:
- Creates multiple train/test splits moving forward in time
- Tests forecast performance on truly unseen future data
- Returns comprehensive accuracy metrics (MAE, RMSE, MAPE, MASE)

**Validation Metrics:**
- **MAE**: Mean Absolute Error
- **RMSE**: Root Mean Squared Error  
- **MAPE**: Mean Absolute Percentage Error
- **MASE**: Mean Absolute Scaled Error (compares to naive forecast)

## Installation & Setup

### Prerequisites
- Python 3.7+
- Dune Analytics API access

### Dependencies

Install required Python packages:

```
pip install flask python-dotenv dune-client
```

### Environment Setup

1. Create a `.env` file in the project root:

```
API_KEY=your_dune_analytics_api_key_here
```

2. Obtain a Dune Analytics API key from dune.com

## Usage Instructions

### Step 1: Data Fetching

```
python app.py
```

- Starts Flask development server on `http://localhost:5000`
- Serves the interactive forecasting dashboard

### Step 3: Use the Dashboard

Navigate to `http://localhost:5000` and interact with:

- **Historical Chart**: Adjust days of historical data to display
- **Projection Chart**: Set forecast horizon (days ahead)
- **Combined Chart**: View history and projections together
- **Validation Info**: Review forecast performance metrics

## File Structure

```
├── getDCBurnByOrg.py # Data fetching from Dune Analytics
├── app.py # Flask backend server
├── templates/
│ └── dashboard.html # Frontend with forecasting algorithms
├── dune_query_result.json # Historical data (generated)
├── .env # Environment variables
└── README.md # This file
```

## Technical Implementation Details

### Data Flow Architecture

1. **Data Ingestion**: getDCBurnByOrg.py fetches from Dune Analytics
2. **Data Serving**: Flask /data endpoint provides JSON API
3. **Data Processing**: JavaScript aggregates hourly to daily data
4. **Model Building**: Comprehensive seasonal model construction
5. **Forecast Generation**: Multi-component projection synthesis
6. **Validation**: Walk-forward cross-validation assessment
7. **Visualization**: Interactive Plotly.js charts

### Key Classes and Their Roles

| Class | Purpose |
|-------|---------|
| SeededRandom | Reproducible random number generation |
| OutlierDetector | Multi-method anomaly identification |
| RobustRegression | Outlier-resistant trend estimation |
| AutocorrelationTester | Statistical significance testing |
| ARModel | Autoregressive modeling with AIC selection |
| TimeSeriesValidator | Performance assessment and metrics |
| SeasonalityDetector | Holiday and calendar pattern recognition |
| BootstrapSampler | Uncertainty quantification |

### Performance Characteristics

- **Computational Complexity**: O(n log n) for most operations
- **Memory Usage**: Linear in data size
- **Forecast Accuracy**: MASE < 1.0 indicates better than naive forecasting
- **Validation Coverage**: Top 10 OUIs by volume for comprehensive assessment

## Validation Results Interpretation

The dashboard displays walk-forward validation metrics:

- **MAE**: Lower values indicate better accuracy
- **MAPE**: Percentage error (< 10% is excellent, < 20% is good)
- **MASE < 1.0**: Better than naive (previous day) forecast ✓
- **Outlier %**: Percentage of data points identified as anomalous

## Future Enhancements

### Algorithmic Improvements
- LSTM/Neural network ensemble methods
- Multivariate modeling (cross-OUI dependencies)
- Real-time model updating
- Confidence interval estimation

### Infrastructure Upgrades
- Database integration (PostgreSQL, TimescaleDB)
- Real-time data streaming (Kafka, WebSocket)
- Containerization (Docker, Kubernetes)
- Production deployment (Gunicorn, nginx)

### Feature Additions
- Alert system for anomaly detection
- Export functionality (PDF reports, CSV)
- Model explainability dashboard
- A/B testing framework for model comparison

## Troubleshooting

### Common Issues

1. **API Key Error**: Ensure .env file contains valid Dune Analytics API key
2. **No Data**: Check if dune_query_result.json exists and contains data
3. **Port Conflict**: Flask default port 5000 may conflict with other services
4. **Memory Issues**: Large datasets may require data chunking or sampling

### Debug Mode

The Flask app runs in debug mode by default:
- Automatic code reloading on changes
- Detailed error pages with stack traces
- Enhanced logging for troubleshooting

## License

This project is intended for educational and research purposes. Please ensure compliance with Dune Analytics terms of service when using their API.

## Contributing

Contributions are welcome! Areas for improvement:
- Additional outlier detection methods
- Alternative regression techniques
- Enhanced seasonal modeling
- Performance optimizations
- Test coverage expansion

---

*This forecasting system demonstrates advanced time series analysis techniques applied to blockchain network data. The combination of robust statistical methods with modern web technologies provides a powerful platform for data-driven decision making.*

