import pandas as pd
import streamlit as st

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.style as style
import matplotlib.font_manager as fm

@st.cache_data
def plot_causalimpact(df: pd.DataFrame):
    # st.altair_chart(causalimpact.plot(impact), use_container_width=True)
    # Create a figure with 3 subplots
    fig, axs = plt.subplots(3, 1, figsize=(6, 10), sharex=True)

    # Plot 1: Line plot
    axs[0].plot(df["Date"], df["observed"], label="Observed")
    axs[0].plot(df["Date"], df["posterior_mean"], label="Predicted (Posterior Mean)")
    axs[0].set_title("Observed vs Predicted", loc="left", # **font_props["title"],
    )
    axs[0].legend(
        loc="upper left", # prop=fm.FontProperties(**font_props["legends"]),
    )

    # Plot 2: Line plot with shading
    axs[1].plot(
        df["Date"], df["point_effects_mean"], label="Mean"
    )
    axs[1].fill_between(
        df["Date"],
        df["point_effects_lower"],
        df["point_effects_upper"],
        alpha=0.3,
        label="Uncertainty",
    )
    axs[1].set_title(
        "Point Effects (Observed - Predicted)", loc="left", #**font_props["title"],
    )
    axs[1].legend(
        loc="upper left", #prop=fm.FontProperties(**font_props["legends"]),
    )

    # Plot 3: Line plot with shading
    axs[2].plot(
        df["Date"],
        df["cumulative_effects_mean"],
        label="Mean",
    )
    axs[2].fill_between(
        df["Date"],
        df["cumulative_effects_lower"],
        df["cumulative_effects_upper"],
        alpha=0.3,
        label="Uncertainty",
    )
    axs[2].tick_params(axis="x", rotation=30)
    axs[2].set_title(
        "Cumulative Lift", loc="left", #**font_props["title"],
    )
    axs[2].legend(loc="upper left", #prop=fm.FontProperties(**font_props["legends"]),
    )

    # Add vertical dotted line at test_start date
    for ax in axs:
        ax.axvline(
            x=df["Date"].loc[df["Date"] == str(st.session_state["test_start"])],
            color="gray",
            linestyle="--",
            label="Test Start",
        )
        ax.axhline(y=0, color="gray", linestyle="-", linewidth=1)

    # Layout adjustments
    fig.tight_layout()

    return fig