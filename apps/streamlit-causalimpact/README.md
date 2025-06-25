# Causal Impact Analysis Tool

A Streamlit application for performing causal impact analysis on marketing campaigns and experiments. This tool provides an intuitive interface for analyzing the incremental effect of interventions using Bayesian structural time-series models.

## Features

- **Multiple Data Input Methods**: Upload CSV files or connect to Kip Query API
- **Interactive Configuration**: Easy-to-use sidebar controls for test setup
- **Parameter Persistence**: Save and load test configurations as JSON files
- **Comprehensive Analysis**: Automated data validation and causal impact modeling
- **Rich Visualizations**: Professional plots showing original vs predicted, pointwise effects, and cumulative impact
- **Multiple Export Formats**: Download results as PNG, CSV, JSON, and Markdown reports
- **Real-time Feedback**: Data validation with clear error messages and warnings

## Installation
Everything is managed via the conda `environment.yml` files:

1. Install the required dependencies using conda create:
    ```bash
    conda env create -f environment.yml
    ```
    Or update the existing anaconda environment:
    ```bash
    conda env update -f environment.yml
    ```
    This will create an Anaconda environment with the correct package dependencies called `streamlit-causalimpact`

2. Activate the new anaconda environment with:
    ```bash
    conda activate streamlit-causalimpact
    ```

## Running the Application

1. Navigate to the directory containing the application files using the `cd` command. 
    
    **Note:** The filepath can differ depending on where you downloaded files.
   ```bash
   cd Documents\GitHub\marketing-analytics\src\experimental-code\streamlit-causalimpact
   ```
2. Start the Streamlit server with the `streamlit run` command referencing the app's file `main.py`:
   ```bash
   streamlit run main.py
   ```
3. Your web browser will likely automatically open to the correct locally hosted URL, but you can also access it at `http://localhost:8501`

## Usage Guide

### 1. Data Input

**Option A: Upload CSV File**
- Click "Choose a CSV file" in the sidebar
- Upload a CSV with columns for date, geography, and metric values

**Option B: Kip Query Integration**
- Select "Kip Query" from the input method dropdown
- Enter your API key and Query ID
- Note: Requires connection to Kepler VPN or WiFi network

**Example Data Structure**:
```csv
Date,State,Sales,Sessions
2024-01-01,California,1000,23000
2024-01-01,Texas,800,19000
2024-01-02,California,1100,27000
2024-01-02,Texas,850,18000
```

### 2. Configuration

**Load Previous Settings (Optional)**
- Expand "Upload Input Parameters JSON" to load saved configurations
- Upload a previously downloaded JSON file to restore all settings

**Column Mapping**
- **Date**: Select the column containing date values
- **Geo**: Select the column containing geographic identifiers
- **Value**: Select the column containing the metric to analyze

**Date Ranges**
- **Pre-Test Start**: Beginning of the baseline period
- **Test Start**: When the intervention began
- **Test End**: When the intervention ended
- **Post-Test End**: End of the analysis period

**Geographic Selection**
- **Test Geos**: Select regions that received the intervention
- **Control Geos**: Select regions that did not receive the intervention

### 3. Analysis Results

The application automatically performs:
- Data validation and quality checks
- Causal impact statistical modeling
- Visualization generation
- Summary statistics calculation

**Key Metrics Displayed:**
- **Incremental Effect**: Additional impact caused by the intervention
- **Test Cell Total**: Total metric value in test regions
- **Control Cell Total**: Predicted metric value without intervention
- **Confidence**: Statistical confidence in the results

### 4. Export Options

**Download Formats Available:**
- **PNG Plot**: High-resolution visualization
- **CSV Results**: Detailed time series data
- **CSV Summary**: Key statistical summaries
- **Markdown Report**: Complete analysis report
- **JSON Settings**: Configuration file for future use

## Data Requirements

### Input Data Format
Your CSV file should contain:
- **Date column**: Date values (any standard format)
- **Geography column**: Geographic identifiers (states, cities, regions, etc.)
- **Value column**: Numeric metric to analyze (sales, conversions, etc.)

### Data Quality Requirements
- A pre-test period 3x the length of the test period is recommended for analysis
- At least one test geography and one control geography
- No missing values in key columns

## Technical Details

### Statistical Method
The application uses Bayesian structural time-series models via the `tfp-causalimpact` ([GitHub](https://github.com/google/tfp-causalimpact)) library to estimate counterfactual outcomes and measure causal effects.

### Performance Optimization
- Cached computations prevent re-analysis on UI interactions
- Session state management for fast parameter changes
- Optimized plot rendering with memory management

### File Structure
```
├── main.py                 # Main application file
├── requirements.txt        # Python dependencies
├── assets/                 # Styling and utility modules
│   ├── kepler_styles.py
│   ├── clean_names.py
│   └── ui.py
└── components/             # Core functionality modules
    ├── data_processor.py
    ├── exports.py
    └── plots.py
```

## Troubleshooting

### Common Issues

**Connection issues with Kip Query**
- Confirm VPN connection to Kepler network
- Verify API key and Query ID are correct

**"ValueError: shape mismatch: objects cannot be broadcast to a single shape. Mismatch is between arg 0 with shape (0,) and arg 1 with shape (2,)."**
- Usually occurs when you're selecting a date that don't "exist" in the dataframe. For example, if you have a weekly dataset and dates start on Sunday, but you select test start to begin on Monday, it won't recognize the date. 
- It's recommended to select the nearest date *before* test launch

**"No valid test/control geos found"**
- Verify geography names match exactly between your selections and data
- Check for typos or extra spaces in geographic identifiers

**"Insufficient data points"**
- Ensure your date range includes enough historical data
- Verify date format is recognized by pandas