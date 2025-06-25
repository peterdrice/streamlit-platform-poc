import io
import streamlit as st
import pandas as pd
import numpy as np

import json

import assets.kepler_styles as kep
import assets.clean_names as janitor
import assets.ui as ui
from components.initialization import initialize_session_state
from components.plots import plot_causalimpact, plot_causalimpact_barplot
from components.data_processor import create_causal_impact_fit, group_data_by_period
from components.exports import (create_markdown_report, create_json_report)

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.style as style
import matplotlib.font_manager as fm
import scipy.stats as stats

from matplotlib import patches as mpatches

import causalimpact
import tensorflow as tf
import tensorflow_probability as tfp

tfd = tfp.distributions

# from streamlit_searchbox import st_searchbox
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
import datetime
from typing import Any, List, Tuple

def search_geos(searchterm: str) -> List[str]:
    return [geo for geo in geos if searchterm.lower() in geo.lower()]

# Initialize session state at the start
initialize_session_state("assets/default_values.json")

# f_title, f_label = kep.load_kepler_fonts()

# Get Streamlit theme
theme = st.get_option("theme.base")

# Define matplotlib styles for light and dark themes
light_style = {
    "bg_color": "#FFFFFF",
    "text_color": "#000000",
    "axis_color": "#666666",
    "grid_color": "#DDDDDD",
}

dark_style = {
    "bg_color": "#101820ff",
    "text_color": "#FFFFFF",
    "axis_color": "#AAAAAA",
    "grid_color": "#444444",
}

# Choose style based on Streamlit theme
if theme == "dark":  # Dark theme
    style = dark_style
else:  # Light theme
    style = light_style

# Update matplotlib stylesheet
mpl.rcParams.update(
    {
        "figure.facecolor": style["bg_color"],
        "axes.facecolor": style["bg_color"],
        "text.color": style["text_color"],
        "axes.labelcolor": style["text_color"],
        "xtick.color": style["text_color"],
        "ytick.color": style["text_color"],
        "grid.color": style["grid_color"],
        "axes.edgecolor": style["axis_color"],
    }
)

# font_props = {
#     "title": {
#         "fontname": "Space Grotesk",
#         "fontsize": 16,
#     },
#     "labels": {
#         "fontname": "Roboto",
#         "fontsize": 10,
#     },
#     "legends": {
#         "family": "Roboto",
#         "size": 8,
#     },
# }

st.set_page_config(
    page_title="Causal Impact",
    page_icon="assets/logos/assets/logos/04-kepler-k-favicon-yellow.png",
    layout="wide",
    menu_items={
    },
)

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

ui.logo("assets/logos/03-kepler-k-bug-lockup-black.png", 
        "assets/logos/02-kepler-k-bug-black.png", 
)


# Sidebar
with st.sidebar:
    st.sidebar.subheader("Configuration")

    input_method = st.selectbox("Select Input Method", ["Upload File", "Kip Query"])
    
    uploaded_file = None
    df = None

    if input_method == "Upload File":
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            uploaded_json = None # restart the upload_json loop on re-upload

    elif input_method == "Kip Query":
        api_key = st.text_input("API Key", type="password")
        query_id = st.text_input("Query ID")
        
        if api_key and query_id:            
            uploaded_file = f"https://kip-query.keplergrp.com/api/queries/{query_id}/results.csv?api_key={api_key}"

            df = pd.read_csv(uploaded_file)
            uploaded_json = None # restart the upload_json loop on re-upload
        
        st.write("**Note:** you must be connected to the Kepler's VPN or connected to a Kepler WiFi network to access files from Kip Query")
    
    # attempt for functionized Kip Query module
    # elif input_method == "Kip Query":
    #     api_key = st.text_input("API Key", type="password")
    #     query_id = st.text_input("Query ID")

    #     col1, col2 = st.columns([2,2])
    #     with col2:
    #         refresh_data = st.button("🔄 Refresh Data", help="Clear cache and fetch fresh data")
        
    #     if refresh_data:
    #         # Clear the cache for this specific query
    #         fetch_kip_query.clear()
    #         st.rerun()
        
    #     if api_key and query_id:
    #         # Fetch data (will use cache if available)
    #         df = fetch_kip_query(api_key, query_id)
            
    #     st.write("**Note:** you must be connected to the Kepler's VPN or connected to a Kepler WiFi network to access files from Kip Query")


    if uploaded_file is not None and df is not None:         
        # Add an option to upload a JSON file
        st.write("### Upload:")
        with st.expander("Upload Input Parameters JSON"):
            uploaded_json = st.file_uploader("Upload File", 
                                             type="json",
            )

        if uploaded_json is not None:
            # Load the uploaded JSON file
            uploaded_data = json.load(uploaded_json)

            st.session_state["test_title_placeholder"] = uploaded_data.get("test_title", "")
            st.session_state["date_col_placeholder"] = uploaded_data.get("date_col", df.columns[0] if len(df.columns) > 0 else "")
            st.session_state["geo_col_placeholder"] = uploaded_data.get("geo_col", df.columns[0] if len(df.columns) > 0 else "")
            st.session_state["value_col_placeholder"] = uploaded_data.get("value_col", df.columns[0] if len(df.columns) > 0 else "")
            st.session_state["grouping_period_placeholder"] = uploaded_data.get("grouping_period", "daily")
            st.session_state["week_start_day_placeholder"] = uploaded_data.get("week_start_day", "monday")

            st.session_state["date_col"] = st.session_state["date_col_placeholder"]
            # Convert date column to datetime and ensure it is called dt
            if st.session_state["date_col"] in df.columns:
                df["dt"] = pd.to_datetime(df[st.session_state["date_col"]])
                # Get min and max dates from the selected date column
                st.session_state["min_date"] = df["dt"].min().date()
                st.session_state["max_date"] = df["dt"].max().date()
            
            st.session_state["pretest_start_placeholder"] = pd.to_datetime(uploaded_data.get("pre_test_start", st.session_state["min_date"]))
            st.session_state["test_start_placeholder"] = pd.to_datetime(uploaded_data.get("test_start", st.session_state["min_date"]))
            st.session_state["test_end_placeholder"] = pd.to_datetime(uploaded_data.get("test_end", st.session_state["max_date"]))
            st.session_state["posttest_end_placeholder"] = pd.to_datetime(uploaded_data.get("post_test_end", st.session_state["max_date"]))

            st.session_state["control_geos_placeholder"] = uploaded_data.get("control_geos", [])
            st.session_state["test_geos_placeholder"] = uploaded_data.get("test_geos", [])
        
        if uploaded_json is None:
            st.session_state["test_title_placeholder"] = ""
            st.session_state["date_col_placeholder"] = df.columns[0] if len(df.columns) > 0 else ""
            st.session_state["geo_col_placeholder"] = df.columns[0] if len(df.columns) > 0 else ""
            st.session_state["value_col_placeholder"] = df.columns[0] if len(df.columns) > 0 else ""
            st.session_state["grouping_period_placeholder"] = "daily"
            st.session_state["week_start_day_placeholder"] = "monday"

            st.session_state["date_col"] = st.session_state["date_col_placeholder"]
            # Convert date column to datetime and ensure it is called dt
            if st.session_state["date_col"] and st.session_state["date_col"] in df.columns:
                df["dt"] = pd.to_datetime(df[st.session_state["date_col"]])

                # Get min and max dates from the selected date column
                st.session_state["min_date"] = df["dt"].min().date()
                st.session_state["max_date"] = df["dt"].max().date()
            else:
                # Set default dates if no valid date column
                today = datetime.date.today()
                st.session_state["min_date"] = today - datetime.timedelta(days=365)
                st.session_state["max_date"] = today

            st.session_state["pretest_start_placeholder"] = st.session_state["min_date"]
            st.session_state["test_start_placeholder"] = st.session_state["min_date"]
            st.session_state["test_end_placeholder"] = st.session_state["max_date"]
            st.session_state["posttest_end_placeholder"] = st.session_state["max_date"]

            st.session_state["control_geos_placeholder"] = []
            st.session_state["test_geos_placeholder"] = []



        # Update the inputs based on the uploaded data
        st.session_state["test_title"] = st.text_input("Test Name:", 
                                                        value=st.session_state["test_title_placeholder"],
        )
        
        # Only show column selectors if we have columns
        if len(df.columns) > 0:
            date_col_index = 0
            if st.session_state["date_col_placeholder"] and st.session_state["date_col_placeholder"] in df.columns:
                date_col_index = df.columns.get_loc(st.session_state["date_col_placeholder"])
            
            st.session_state["date_col"] = st.selectbox("Date", 
                                                        index=date_col_index,
                                                        options=df.columns,
            )
            
            geo_col_index = 0
            if st.session_state["geo_col_placeholder"] and st.session_state["geo_col_placeholder"] in df.columns:
                geo_col_index = df.columns.get_loc(st.session_state["geo_col_placeholder"])
            
            st.session_state["geo_col"] = st.selectbox("Geo", 
                                                        index=geo_col_index,
                                                        options=df.columns,
            )
            
            value_col_index = 0
            if st.session_state["value_col_placeholder"] and st.session_state["value_col_placeholder"] in df.columns:
                value_col_index = df.columns.get_loc(st.session_state["value_col_placeholder"])
            
            st.session_state["value_col"] = st.selectbox("Value", 
                                                            index=value_col_index,
                                                            options=df.columns,
            )

        # Add grouping period selector
        st.write("## Data Aggregation:")
        grouping_options = ["daily", "weekly", "monthly", "quarterly", "yearly"]
        grouping_index = 0
        if st.session_state["grouping_period_placeholder"] in grouping_options:
            grouping_index = grouping_options.index(st.session_state["grouping_period_placeholder"])
        
        st.session_state["grouping_period"] = st.selectbox(
            "Group data by:",
            options=grouping_options,
            index=grouping_index,
            help="Choose how to aggregate your data over time."
        )
        
        # Add week start day selector (only show if weekly is selected)
        if st.session_state["grouping_period"] == "weekly":
            week_start_options = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            week_start_index = 0
            if st.session_state["week_start_day_placeholder"] in week_start_options:
                week_start_index = week_start_options.index(st.session_state["week_start_day_placeholder"])
            
            st.session_state["week_start_day"] = st.selectbox(
                "Week starts on:",
                options=week_start_options,
                index=week_start_index,
                help="Choose which day of the week to start your weekly periods."
            )
        else:
            # Display the actual periods that will be used
            if st.session_state["grouping_period"] != "daily":
                st.write("**Actual periods that will be used:**")
                
                def get_period_for_date(date_val, grouping_period, week_start_day=None):
                    """Get the actual period start date for a given date"""
                    temp_df = pd.DataFrame({'date': [pd.Timestamp(date_val)]})
                    grouped = group_data_by_period(temp_df, 'date', grouping_period, week_start_day)
                    return grouped['period'].iloc[0]
                
                week_start = st.session_state.get("week_start_day", "monday") if st.session_state["grouping_period"] == "weekly" else None
                
                actual_pre_start = get_period_for_date(st.session_state["pre_test_start"], st.session_state["grouping_period"], week_start)
                actual_test_start = get_period_for_date(st.session_state["test_start"], st.session_state["grouping_period"], week_start)
                actual_test_end = get_period_for_date(st.session_state["test_end"], st.session_state["grouping_period"], week_start)
                actual_post_end = get_period_for_date(st.session_state["post_test_end"], st.session_state["grouping_period"], week_start)
                
                st.info(f"""
                **Pre-test period:** {actual_pre_start} to {get_period_for_date(st.session_state["pre_test_end"], st.session_state["grouping_period"], week_start)}
                
                **Test period:** {actual_test_start} to {actual_post_end}
                """)
            
            # Store the actual periods for later use
            if st.session_state["grouping_period"] != "daily":
                st.session_state["actual_periods_calculated"] = True

        st.write("## Date Ranges:")
        
        # Dynamic labels based on grouping period
        if st.session_state["grouping_period"] == "daily":
            pre_start_label = "Pre-Test Start Date"
            test_start_label = "Test Start Date" 
            test_end_label = "Test End Date"
            post_end_label = "Post-Test End Date"
            date_help = "Select specific dates for analysis"
        elif st.session_state["grouping_period"] == "weekly":
            pre_start_label = "Pre-Test Start (Week Containing)"
            test_start_label = "Test Start (Week Containing)"
            test_end_label = "Test End (Week Containing)"
            post_end_label = "Post-Test End (Week Containing)"
            week_start_day = st.session_state.get("week_start_day", "monday").title()
            date_help = f"Select any date - the {week_start_day}-starting week containing this date will be used"
        elif st.session_state["grouping_period"] == "monthly":
            pre_start_label = "Pre-Test Start (Month Containing)"
            test_start_label = "Test Start (Month Containing)"
            test_end_label = "Test End (Month Containing)"
            post_end_label = "Post-Test End (Month Containing)"
            date_help = "Select any date - the month containing this date will be used"
        elif st.session_state["grouping_period"] == "quarterly":
            pre_start_label = "Pre-Test Start (Quarter Containing)"
            test_start_label = "Test Start (Quarter Containing)"
            test_end_label = "Test End (Quarter Containing)"
            post_end_label = "Post-Test End (Quarter Containing)"
            date_help = "Select any date - the quarter containing this date will be used"
        else:  # yearly
            pre_start_label = "Pre-Test Start (Year Containing)"
            test_start_label = "Test Start (Year Containing)"
            test_end_label = "Test End (Year Containing)"
            post_end_label = "Post-Test End (Year Containing)"
            date_help = "Select any date - the year containing this date will be used"
        
        st.session_state["pre_test_start"] = st.date_input(
            pre_start_label,
            value=st.session_state["pretest_start_placeholder"],
            min_value=st.session_state["min_date"],
            max_value=st.session_state["max_date"],
            help=date_help
        )
        st.session_state["test_start"] = st.date_input(
            test_start_label,
            value=st.session_state["test_start_placeholder"],
            min_value=st.session_state["min_date"],
            max_value=st.session_state["max_date"],
            help=date_help
        )
        st.session_state["test_end"] = st.date_input(
            test_end_label,
            value=st.session_state["test_end_placeholder"],
            min_value=st.session_state["min_date"],
            max_value=st.session_state["max_date"],
            help=date_help
        )
        st.session_state["post_test_end"] = st.date_input(
            post_end_label,
            value=st.session_state["posttest_end_placeholder"],
            min_value=st.session_state["min_date"],
            max_value=st.session_state["max_date"],
            help=date_help
        )

        # Only show geo selectors if we have the geo column
        if st.session_state["geo_col"] and st.session_state["geo_col"] in df.columns:
            geos = df.sort_values(st.session_state["geo_col"])[st.session_state["geo_col"]].unique().tolist()

            st.session_state["test_geos"] = st.multiselect(
                label="Select test geos",
                options=geos,
                default=st.session_state["test_geos_placeholder"],
            )
            st.session_state["control_geos"] = st.multiselect(
                label="Choose control geos",
                options=geos,
                default=st.session_state["control_geos_placeholder"],
            )

        st.session_state["pre_test_end"] = st.session_state["test_start"] - datetime.timedelta(days=1)
            
        # Mapping and Display (assuming date is in datetime format)
        if st.session_state["date_col"] and st.session_state["geo_col"] and st.session_state["value_col"]:
            mapped_df = (
                df[[st.session_state["date_col"], st.session_state["geo_col"], st.session_state["value_col"]]]
            )

            mapped_df.columns = [
                "Date",
                "Geo",
                "Value",
            ]
    
    # Only show download section if we have valid session state
    if st.session_state.get("test_title") is not None:
        st.write("### Download Test Parameters:")
        st.write("Preserve these parameters to quickly load them next time.")

        # Save the inputs into a dictionary
        input_dict = {
            "test_title": st.session_state.get("test_title", ""),
            "date_col": st.session_state.get("date_col", ""),
            "geo_col": st.session_state.get("geo_col", ""),
            "value_col": st.session_state.get("value_col", ""),
            "grouping_period": st.session_state.get("grouping_period", "daily"),
            "week_start_day": st.session_state.get("week_start_day", "monday"),
            "pre_test_start": str(st.session_state.get("pre_test_start", "")).split()[0] if st.session_state.get("pre_test_start") else "",
            "test_start": str(st.session_state.get("test_start", "")).split()[0] if st.session_state.get("test_start") else "",
            "test_end": str(st.session_state.get("test_end", "")).split()[0] if st.session_state.get("test_end") else "",
            "post_test_end": str(st.session_state.get("post_test_end", "")).split()[0] if st.session_state.get("post_test_end") else "",
            "test_geos": st.session_state.get("test_geos", []),
            "control_geos": st.session_state.get("control_geos", []),
        }

        # Convert the dictionary to a JSON string
        json_str = json.dumps(input_dict, indent=2)

        # To write the JSON string to a file, you can use:
        # with open('test_inputs.json', 'w') as file:
        #     file.write(json_str)

        st.download_button(
            label="Download JSON",
            data=json_str,
            file_name=f'{st.session_state["test_title"].replace(" ", "_").lower()}_inputs.json',
            mime="application/json",
        )


# Main Content

# Define all session_state vars
required_keys = ["date_col", "geo_col", "value_col", "pre_test_start", "test_start", "test_end", "post_test_end", "test_geos", "control_geos"]

# Check if we have all required keys AND they have valid values (not None/empty)
if (all(key in st.session_state for key in required_keys) and 
    all(st.session_state[key] is not None for key in required_keys) and
    st.session_state["test_geos"] and st.session_state["control_geos"] and
    "mapped_df" in locals()):

    try:
        # Data validation
        st.write("### Data Validation")

        # Check if we have data for selected geos
        available_geos = mapped_df["Geo"].unique().tolist()
        missing_test_geos = [geo for geo in st.session_state["test_geos"] if geo not in available_geos]
        missing_control_geos = [geo for geo in st.session_state["control_geos"] if geo not in available_geos]

        if missing_test_geos:
            st.error(f"Test geos not found in data: {missing_test_geos}")
        if missing_control_geos:
            st.error(f"Control geos not found in data: {missing_control_geos}")

        # Filter out missing geos
        valid_test_geos = [geo for geo in st.session_state["test_geos"] if geo in available_geos]
        valid_control_geos = [geo for geo in st.session_state["control_geos"] if geo in available_geos]

        if not valid_test_geos:
            st.error("No valid test geos found in the data. Please check your geo selection.")
            st.stop()
        if not valid_control_geos:
            st.error("No valid control geos found in the data. Please check your geo selection.")
            st.stop()

        # Apply date grouping to the data before filtering
        mapped_df["Date"] = pd.to_datetime(mapped_df["Date"])
        
        if st.session_state["grouping_period"] != "daily":
            # Group data by the selected period
            week_start = st.session_state.get("week_start_day", "monday") if st.session_state["grouping_period"] == "weekly" else None
            grouped_mapped_df = group_data_by_period(mapped_df, "Date", st.session_state["grouping_period"], week_start)
            
            # Aggregate by the new period
            mapped_df = (
                grouped_mapped_df
                .groupby(["period", "Geo"], as_index=False)
                .agg({"Value": "sum"})
                .rename(columns={"period": "Date"})
            )
            mapped_df["Date"] = pd.to_datetime(mapped_df["Date"])

        # Regroup and sum data at the selected time level
        filtered_data = mapped_df[mapped_df["Geo"].isin(valid_test_geos + valid_control_geos)]

        if filtered_data.empty:
            st.error("No data found for selected geos. Please check your selections.")
            st.stop()

        grouped_df = (
            filtered_data
            .assign(Geo=filtered_data["Geo"].apply(lambda x: "test" if x in valid_test_geos else x))
            .groupby(["Date", "Geo"])
            .sum()
            .sort_values("Date", ascending=False)
        )

        if grouped_df.empty:
            st.error("No data after grouping. Please check your date and geo selections.")
            st.stop()

        # Pivot wider dataframe for Causal Impact
        pivot_df = (
            grouped_df.pivot_table(index="Date", columns="Geo", values="Value", fill_value=0)
        ).reset_index()

        pivot_df.columns.name = None

        # Ensure we have the required columns
        required_columns = ["Date", "test"] + valid_control_geos
        missing_columns = [col for col in required_columns if col not in pivot_df.columns]

        if missing_columns:
            st.error(f"Missing required columns after pivot: {missing_columns}")
            st.stop()

        pivot_df = pivot_df[required_columns]
        pivot_df["Date"] = pd.to_datetime(pivot_df["Date"], format="%Y-%m-%d")
        pivot_df = pivot_df.set_index("Date")

        # Validate date ranges - need to be more flexible with period boundaries
        data_start_date = pivot_df.index.min().date()
        data_end_date = pivot_df.index.max().date()

        # For period-based data, we need to check if the selected dates fall within reasonable ranges
        # rather than exact matches, since period start dates might not align with user selections
        if st.session_state["grouping_period"] != "daily":
            # Create a more flexible date range check for aggregated data
            if st.session_state["pre_test_start"] < data_start_date:
                st.warning(f'Pre-test start date ({st.session_state["pre_test_start"]}) is before available data ({data_start_date}). Using closest available period.')
            if st.session_state["post_test_end"] > data_end_date:
                st.warning(f'Post-test end date ({st.session_state["post_test_end"]}) is after available data ({data_end_date}). Using closest available period.')
        else:
            # Original exact date validation for daily data
            if st.session_state["pre_test_start"] < data_start_date:
                st.warning(f'Pre-test start date ({st.session_state["pre_test_start"]}) is before available data ({data_start_date})')
            if st.session_state["post_test_end"] > data_end_date:
                st.warning(f'Post-test end date ({st.session_state["post_test_end"]}) is after available data ({data_end_date})')

        # For period data, use more flexible date range selection
        if st.session_state["grouping_period"] != "daily":
            # Find the periods that best encompass the selected date ranges
            available_dates = sorted(pivot_df.index.date)
            
            # Find closest period start for pre-test
            pre_start_candidates = [d for d in available_dates if d <= st.session_state["pre_test_start"]]
            if pre_start_candidates:
                actual_pre_start = max(pre_start_candidates)
            else:
                actual_pre_start = min(available_dates)
            
            # Find closest period for pre-test end
            pre_end_candidates = [d for d in available_dates if d <= st.session_state["pre_test_end"]]
            if pre_end_candidates:
                actual_pre_end = max(pre_end_candidates)
            else:
                actual_pre_end = actual_pre_start
            
            # Find closest period start for test period
            test_start_candidates = [d for d in available_dates if d >= st.session_state["test_start"]]
            if test_start_candidates:
                actual_test_start = min(test_start_candidates)
            else:
                actual_test_start = min(available_dates)
            
            # Find closest period for post-test end
            test_end_candidates = [d for d in available_dates if d <= st.session_state["post_test_end"]]
            if test_end_candidates:
                actual_test_end = max(test_end_candidates)
            else:
                actual_test_end = max(available_dates)
            
            # Use the adjusted dates for period selection
            pre_period_data = pivot_df.loc[str(actual_pre_start):str(actual_pre_end)]
            post_period_data = pivot_df.loc[str(actual_test_start):str(actual_test_end)]
            
            # Update the periods for causal impact
            pre_period = (str(actual_pre_start), str(actual_pre_end))
            post_period = (str(actual_test_start), str(actual_test_end))
            
        else:
            # Original logic for daily data
            pre_period_data = pivot_df.loc[str(st.session_state["pre_test_start"]):str(st.session_state["pre_test_end"])]
            post_period_data = pivot_df.loc[str(st.session_state["test_start"]):str(st.session_state["post_test_end"])]
            pre_period = (str(st.session_state["pre_test_start"]), str(st.session_state["pre_test_end"]))
            post_period = (str(st.session_state["test_start"]), str(st.session_state["post_test_end"]))

        if len(pre_period_data) < 2:
            st.error(f"Insufficient pre-period data: {len(pre_period_data)} rows. Need at least 2 data points.")
            st.stop()
        if len(post_period_data) < 1:
            st.error(f"Insufficient post-period data: {len(post_period_data)} rows. Need at least 1 data point.")
            st.stop()

        # Display grouping information
        def get_week_end_day(start_day):
            """Get the end day of week given start day"""
            days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            start_idx = days.index(start_day.lower())
            end_idx = (start_idx + 6) % 7
            return days[end_idx].title()
        
        grouping_display = {
            "daily": "Daily",
            "weekly": f"Weekly ({st.session_state.get('week_start_day', 'monday').title()}-{get_week_end_day(st.session_state.get('week_start_day', 'monday'))})",
            "monthly": "Monthly (Start of Month)",
            "quarterly": "Quarterly (Start of Quarter)", 
            "yearly": "Yearly (Start of Year)"
        }
        
        st.success(f"Data validation passed. Aggregation: {grouping_display[st.session_state['grouping_period']]}. Pre-period: {len(pre_period_data)} rows, Post-period: {len(post_period_data)} rows")

        # Run Causal Impact with the determined periods
        impact = create_causal_impact_fit(
            pivot_df=pivot_df, pre_period=pre_period, post_period=post_period
        )
        impact_df = impact.series.reset_index()

        # Check if we have results
        if impact_df.empty:
            st.error("Causal impact analysis returned no results.")
            st.stop()

    except Exception as e:
        st.error(f"Error in causal impact analysis: {str(e)}")
        st.write("Please check your data and parameters.")
        st.write("**Debug information:**")
        st.write(f'- Available geos in data: {mapped_df["Geo"].unique().tolist() if "mapped_df" in locals() else "No data"}')
        st.write(f'- Selected test geos: {st.session_state["test_geos"]}')
        st.write(f'- Selected control geos: {st.session_state["control_geos"]}')
        st.write(f'- Date range in data: {mapped_df["Date"].min()} to {mapped_df["Date"].max() if "mapped_df" in locals() else "No data"}')
        st.write(f'- Selected date range: {st.session_state["pre_test_start"]} to {st.session_state["post_test_end"]}')
        st.write(f'- Grouping period: {st.session_state["grouping_period"]}')
        st.stop()

    # If we get here, the analysis was successful
    mpl_data = impact.series.reset_index()

    st.write(f'## {st.session_state["test_title"]}')

    # Results
    col_effect, col_pval, col_prefitr2, col_test, col_control = st.columns(5)
    col_effect.metric(
        label=f'Incremental {st.session_state["value_col"]}', 
        value=f'{impact.summary.abs_effect["cumulative"]:,.0f}', 
        delta=f'{impact.summary.rel_effect["cumulative"]:.2%}',
        help=f'The incremental `{st.session_state["value_col"]}` generated as a result of the test',
        border=True,
    )
    col_pval.metric(
        label="Confidence interval", 
        value=f"{1-impact.summary.p_value['cumulative']:.0%}",
        help="The posterior probability of a causal effect. Should be >80%, 90%, or 95% in most cases",
        border=True,
    )
    col_prefitr2.metric(
        label="Pre-Test R²",
        value=f'{r2_score(
            mpl_data[(mpl_data["Date"] >= pd.to_datetime(st.session_state["pre_test_start"]))
                      & (mpl_data["Date"] <= pd.to_datetime(st.session_state["pre_test_end"]))
                    ]["observed"], 
            mpl_data[(mpl_data["Date"] >= pd.to_datetime(st.session_state["pre_test_start"]))
                      & (mpl_data["Date"] <= pd.to_datetime(st.session_state["pre_test_end"]))
                    ]["posterior_mean"],
        ):.02%}',
        help="The the model's R² during the pre-test window",
        border=True,
    )
    col_test.metric(
        label="Test Cell Total", 
        value=f"{impact.summary.actual['cumulative']:,.0f}",
        help=f"The `test` group's total `{st.session_state['value_col']}`",
        border=True,
    )
    col_control.metric(
        label="Control Cell Total", 
        value=f"{impact.summary.predicted['cumulative']:,.0f}",
        help=f"The `control` group's total `{st.session_state['value_col']}`",
        border=True,
    )

    # Create results data structure
    results_data = {
        "test_name": st.session_state["test_title"],
        "grouping_period": st.session_state["grouping_period"],
        "pre_test_period": {
            "start": str(st.session_state["pre_test_start"]),
            "end": str(st.session_state["pre_test_end"])
        },
        "test_period": {
            "start": str(st.session_state["test_start"]),
            "end": str(st.session_state["test_end"])
        },
        "post_test_period": {
            "start": str(st.session_state["test_start"]),
            "end": str(st.session_state["post_test_end"])
        },
        "incremental_results": {
            "absolute_effect": f'{impact.summary.abs_effect["cumulative"]:,.0f}',
            "relative_effect": f'{impact.summary.rel_effect["cumulative"]:,.2%}',
            "test_cell_total": f'{impact.summary.actual["cumulative"]:,.2f}',
            "control_cell_total": f'{impact.summary.predicted["cumulative"]:,.2f}'
        },
        "confidence": f'{(1 - impact.summary.p_value["cumulative"]):,.2%}',
        "analysis_date": str(datetime.date.today())
    }

    # Create JSON string
    json_results = json.dumps(results_data, indent=2)

    colleft, colright = st.columns(2)
    with colleft:
        tab1, tab2 = st.tabs(["Line Plot", "Bar Plot"])
        
        with tab1:
            fig_causalimpact_lineplot = plot_causalimpact(mpl_data)
            st.pyplot(fig_causalimpact_lineplot)
        with tab2:
            fig_causalimpact_barplot = plot_causalimpact_barplot(
                impact_summary=impact.summary, 
                value_col=st.session_state["value_col"],
            )
            st.pyplot(fig_causalimpact_barplot)

    with colright:
        st.write("### Test Results:")
        def create_plot_buffer():
            buf = io.BytesIO()
            fig_causalimpact_lineplot.savefig(buf, format="png", dpi=300, bbox_inches="tight")
            buf.seek(0)
            return buf.getvalue()

        st.download_button(
            label="Download Plot (PNG)",
            data=create_plot_buffer(),
            file_name=f'{st.session_state["test_title"].replace(" ", "_").lower()}_results.png',
            mime="image/png", 
            icon=":material/download:",
            help="Download analysis result plots", 
        )
        st.download_button(
            label="Download Results (CSV)",
            data=impact.series.to_csv(index=True).encode("utf-8"),
            file_name=f'{st.session_state["test_title"].replace(" ", "_").lower()}_results.csv',
            mime="text/csv",
            icon=":material/download:",
            help="Download analysis results in CSV format"
        )
        st.download_button(
            label="Download Summary Results Summary (CSV)",
            data=impact.summary.to_csv(index=True).encode("utf-8"),
            file_name=f'{st.session_state["test_title"].replace(" ", "_").lower()}_results_summary.csv',
            mime="text/csv",
            icon=":material/download:",
            help="Download analysis summary in CSV format"
        )
        # st.download_button(
        #     label="Download Results (JSON)",
        #     data=create_json_report(
        #         test_title=st.session_state["test_title"],
        #         value_col=st.session_state["value_col"],
        #         pre_test_start=st.session_state["pre_test_start"],
        #         pre_test_end=st.session_state["pre_test_end"],
        #         test_start=st.session_state["test_start"],
        #         test_end=st.session_state["test_end"],
        #         post_test_end=st.session_state["post_test_end"],
        #         # test_geos=st.session_state["test_geos"],
        #         # control_geos=st.session_state["control_geos"],
        #         impact_summary=impact.summary,  # Your cached results dict
        #     ),
        #     file_name=f'{st.session_state["test_title"].replace(" ", "_").lower()}_results.json',
        #     mime="application/json",
        #     icon=":material/download:",
        #     help="Download analysis results in JSON format"
        # )
        st.download_button(
            label="Download Report (Markdown)",
            data=create_markdown_report(
                test_title=st.session_state["test_title"],
                value_col=st.session_state["value_col"],
                pre_test_start=st.session_state["pre_test_start"],
                pre_test_end=st.session_state["pre_test_end"],
                test_start=st.session_state["test_start"],
                test_end=st.session_state["test_end"],
                post_test_end=st.session_state["post_test_end"],
                test_geos=st.session_state["test_geos"],
                control_geos=st.session_state["control_geos"],
                impact_summary=impact.summary,  # Your cached results dict
                detailed_report=causalimpact.summary(impact, output_format="report")
            ),
            file_name=f'{st.session_state["test_title"].replace(" ", "_").lower()}_report.md',
            mime="text/markdown",
            icon=":material/download:",
            help="Download complete analysis report in Markdown format"
        )
        st.download_button(
            label="Download Configuration (JSON)",
            data=json_str,
            file_name=f'{st.session_state["test_title"].replace(" ", "_").lower()}_inputs.json',
            mime="application/json",
            help="Download to preserve app settings for future readouts",
        )
        with st.expander("See summary"):
            st.markdown(causalimpact.summary(impact, output_format="summary"))
        with st.expander("See report"):
            st.markdown(causalimpact.summary(impact, output_format="report"))
        st.write("### Test Parameters:")
        col_pretest, col_posttest = st.columns(2)
        col_pretest.markdown(
            f"""
            **Pre-Test Period:**\
            
            Start: {str(st.session_state["pre_test_start"]).split()[0]}\
            
            End: {str(st.session_state["pre_test_end"]).split()[0]}
            """
        )
        col_posttest.markdown(
            f"""
            **Test Period:**\
            
            Start: {str(st.session_state["test_start"]).split()[0]}\
            
            End: {str(st.session_state["post_test_end"]).split()[0]}
            """
        )
        
        # Display grouping information
        st.markdown(
            f"""
            **Data Aggregation:** {grouping_display[st.session_state["grouping_period"]]}
            """
        )

    st.markdown(
        f"""
        ### Dataframes:
        """
    )

    tab_inputdf, tab_outputdf, tab_summarydf = st.tabs(["Input Data", "Output Data", "Summary Data"])
    with tab_inputdf:
        st.dataframe(pivot_df, use_container_width=True)
    with tab_outputdf:
        st.dataframe(impact.series, use_container_width=True)
    with tab_summarydf:
        st.dataframe(impact.summary, use_container_width=True)

else:
    st.write("## Welcome to Causal Impact Analysis")
    st.write("Please upload a CSV file or connect a Kip Query result to get started.")