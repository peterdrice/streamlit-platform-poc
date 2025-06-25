import streamlit as st
import pandas as pd
import os

import assets.kepler_styles as kep
import assets.clean_names as janitor
import assets.ui as ui

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

st.set_page_config(
    page_title="Kip MMM Processor",
    page_icon="assets/logos/assets/logos/04-kepler-k-favicon-yellow.png",
    layout="wide",
    menu_items={},
)

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

ui.logo("assets/logos/03-kepler-k-bug-lockup-black.png", 
        "assets/logos/02-kepler-k-bug-black.png", 
)

# Sidebar configuration
with st.sidebar:
    st.subheader("Configuration")

    # File uploads
    pareto_alldecomp_matrix = st.file_uploader(
        "Upload Pareto Alldecomp Matrix CSV", type="csv", key="pareto_matrix"
    )
    pareto_agg = st.file_uploader(
        "Upload Pareto Aggregated CSV", type="csv", key="pareto_agg"
    )
    raw_data = st.file_uploader("Upload Raw Data CSV", type="csv", key="raw_data")
    media_transform = st.file_uploader(
        "Upload Media Transform CSV", type="csv", key="media_transform"
    )

# Process data when all required files are uploaded
if pareto_alldecomp_matrix:

    # Process Pareto Matrix
    pareto_df = pd.read_csv(pareto_alldecomp_matrix)

    # Input parameters
    # sol_id = st.text_input("Solution ID", value="3_275_3")
    sol_id = st.selectbox("SolID", 
                 options=(
                     pareto_df[pareto_df["top_sol"] == True]["solID"].unique()
                 ),
            )
    kpi = st.text_input("KPI", value="valid_outsidesales_meetingrequest")

    pareto_df = (
        pareto_df.drop(columns=["Unnamed: 0"])
        .query(f"solID == '{sol_id}'")
        .assign(source=kpi)
    )

    pareto_decomp_matrix_ordered_cols = [
        "source",
        "solID",
        "ds",
        "dep_var",
        "depVarHat",
        "intercept",
    ]
    pareto_decomp_matrix_remaining_cols = [
        col for col in pareto_df.columns if col not in pareto_decomp_matrix_ordered_cols
    ]
    pareto_df = pareto_df[
        pareto_decomp_matrix_ordered_cols + pareto_decomp_matrix_remaining_cols
    ]

    st.subheader("Pareto All Decomp Matrix Data")
    st.download_button(
        label="Download Pareto Alldecomp Matrix",
        data=pareto_df.to_csv(index=False),
        file_name=f"{sol_id}_output.csv",
        mime="text/csv",
    )
    st.dataframe(pareto_df)


if pareto_agg:

    # Process Pareto Aggregated
    pareto_agg_df = pd.read_csv(pareto_agg)
    pareto_agg_df = (
        pareto_agg_df.drop(columns=["Unnamed: 0"])
        .query(f"solID == '{sol_id}'")
        .assign(source=kpi)
    )

    pareto_agg_ordered_cols = ["source", "solID"]
    pareto_agg_remaining_cols = [
        col for col in pareto_agg_df.columns if col not in pareto_agg_ordered_cols
    ]

    pareto_agg_df = pareto_agg_df[pareto_agg_ordered_cols + pareto_agg_remaining_cols]

    st.subheader("Pareto Aggregated Data")
    st.dataframe(pareto_agg_df)

if raw_data:
    
    # Process Raw Data
    raw_df = pd.read_csv(raw_data).drop(columns=["Unnamed: 0"])

    st.subheader("Raw Data")
    st.dataframe(raw_df)

    # Process Response Data
    value_cols = list(
        pareto_df.drop(columns=["solID", "cluster", "top_sol", "source"]).columns
    )

    pareto_response_df = (
        pareto_df.melt(id_vars="ds", value_vars=value_cols)
        .assign(
            variable=lambda df: df["variable"].apply(lambda x: x.replace("_spend", "")),
            solID=sol_id,
            kpi=kpi,
        )
        .rename(columns={"value": "response"})
    )

    # st.subheader("Response Data")
    # st.dataframe(pareto_response_df)

    # Process Spend Data
    spend_cols = raw_df.filter(regex="spend").columns
    raw_spend_df = (
        raw_df.melt(id_vars=["dt"], value_vars=spend_cols)
        .assign(
            variable=lambda df: df["variable"].apply(lambda x: x.replace("_spend", "")),
            solID=sol_id,
            kpi=kpi,
        )
        .rename(columns={"value": "spend"})
    )

    # st.subheader("Spend Data")
    # st.dataframe(raw_spend_df)

    # Process Impressions Data
    imps_cols = raw_df.filter(regex="impressions").columns
    raw_imps_df = (
        raw_df.melt(id_vars=["dt"], value_vars=imps_cols)
        .assign(
            variable=lambda df: df["variable"].apply(
                lambda x: x.replace("_impressions", "")
            ),
            solID=sol_id,
            kpi=kpi,
        )
        .rename(columns={"value": "impressions"})
    )

    # st.subheader("Impressions Data")
    # st.dataframe(raw_imps_df)

    # Create merged dataset
    merge_df = (
        pareto_response_df[["kpi", "solID", "ds", "variable", "response"]]
        .rename(columns={"ds": "dt", "value": "conversions"})
        .merge(
            raw_spend_df,
            on=["kpi", "solID", "dt", "variable"],
            how="outer",
        )
        .merge(
            raw_imps_df,
            on=["kpi", "solID", "dt", "variable"],
            how="outer",
        )
    )

    st.subheader("Merged Data")
    st.download_button(
        label="Download Merged Data",
        data=merge_df.to_csv(index=False),
        file_name=f"{sol_id}_merge_df.csv",
        mime="text/csv",
    )
    st.dataframe(merge_df)

    # Create summary
    summary_df = (
        merge_df
        .drop("dt", axis=1)
        .groupby(["kpi", "solID", "variable"])
        .sum()
        .reset_index()
    )

    st.subheader("Summary Data")
    st.download_button(
        label="Download Summary Data",
        data=summary_df.to_csv(index=False),
        file_name=f"{sol_id}_summary_df.csv",
        mime="text/csv",
    )
    st.dataframe(summary_df)

if media_transform:

    # Process Pareto Aggregated
    media_transform_df = pd.read_csv(media_transform)
    media_transform_df = (
        media_transform_df.drop(columns=["Unnamed: 0"])
        .query(f"solID == '{sol_id}'")
        .assign(source=kpi)
    )

    media_transform_ordered_cols = ["source", "solID"]
    media_transform_remaining_cols = [
        col for col in media_transform_df.columns if col not in media_transform_ordered_cols
    ]

    media_transform_df = media_transform_df[media_transform_ordered_cols + media_transform_remaining_cols]

    st.subheader("Media Transform Matrix Data")
    st.dataframe(media_transform_df)


else:
    st.write("## Welcome to Kip MMM Data Processing")
    st.write("Please upload a CSV file")
