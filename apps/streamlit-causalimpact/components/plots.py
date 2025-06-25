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
    axs[0].set_title(
        "Observed vs Predicted",
        loc="left",  # **font_props["title"],
    )
    axs[0].legend(
        loc="upper left",  # prop=fm.FontProperties(**font_props["legends"]),
    )

    # Plot 2: Line plot with shading
    axs[1].plot(df["Date"], df["point_effects_mean"], label="Mean")
    axs[1].fill_between(
        df["Date"],
        df["point_effects_lower"],
        df["point_effects_upper"],
        alpha=0.3,
        label="Uncertainty",
    )
    axs[1].set_title(
        "Point Effects (Observed - Predicted)",
        loc="left",  # **font_props["title"],
    )
    axs[1].legend(
        loc="upper left",  # prop=fm.FontProperties(**font_props["legends"]),
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
        "Cumulative Lift",
        loc="left",  # **font_props["title"],
    )
    axs[2].legend(
        loc="upper left",  # prop=fm.FontProperties(**font_props["legends"]),
    )

    # Find the actual test start date in the data
    # This handles cases where the session_state date might not exactly match
    # the dates in the aggregated dataframe (e.g., for weekly/monthly data)
    try:
        test_start_target = pd.to_datetime(st.session_state["test_start"])
        df_dates = pd.to_datetime(df["Date"])

        # Find the closest date in the dataframe that is >= test_start
        valid_dates = df_dates[df_dates >= test_start_target]
        if len(valid_dates) > 0:
            actual_test_start = valid_dates.min()
        else:
            # If no dates are >= test_start, use the closest date
            actual_test_start = df_dates.iloc[
                (df_dates - test_start_target).abs().argsort()[0]
            ]

        # Add vertical dotted line at actual test start date
        for ax in axs:
            ax.axvline(
                x=actual_test_start,
                color="gray",
                linestyle="--",
                alpha=0.7,
                label="Test Start",
            )
            ax.axhline(y=0, color="gray", linestyle="-", linewidth=1, alpha=0.5)

    except (KeyError, IndexError, ValueError) as e:
        # If there's any issue finding the test start date, skip the vertical line
        # but still add the horizontal zero line
        for ax in axs:
            ax.axhline(y=0, color="gray", linestyle="-", linewidth=1, alpha=0.5)

        # Optionally log the error for debugging
        st.warning(f"Could not add test start line to plot: {str(e)}")

    # Layout adjustments
    fig.tight_layout()

    return fig


@st.cache_data
def plot_causalimpact_barplot(impact_summary, value_col):
    """
    Create a bar plot comparing observed vs predicted (posterior mean) values
    with percent lift annotation

    Args:
        impact_summary: Causal impact summary object with actual and predicted values
        test_geos: List of test geo names
        control_geos: List of control geo names
        value_col: Name of the value column for labeling

    Returns:
        matplotlib figure
    """

    # Extract the cumulative values from the impact summary
    observed_total = impact_summary.actual["cumulative"]
    predicted_total = impact_summary.predicted["cumulative"]

    print(impact_summary)

    # Calculate percent lift
    percent_lift = impact_summary.rel_effect["cumulative"] * 100

    # Create figure and axis
    fig, ax = plt.subplots(1, 1, figsize=(6, 6))

    # Define colors - matching the style in your reference image
    # control_color = '#2E4057'  # Dark blue
    # test_color = '#2E4057'     # Dark blue for base
    # lift_color = '#1DD1A1'     # Bright green for lift

    # Bar positions
    x_pos = [
        0,
        1,
    ]
    bar_width = 0.6

    # Create the bars
    control_bar = ax.bar(
        x_pos[0],
        predicted_total,
        bar_width,
        # color=control_color,
        label="Predicted (Control)",
    )

    # lift_bar = ax.bar(
    #     x_pos[2],
    #     predicted_total,
    #     bottom=observed_total - predicted_total,
    #     bar_width,
    #     # color=control_color,
    #     label="Lift",
    # )

    # For the test bar, show the predicted portion in dark blue and lift in green
    test_base_bar = ax.bar(
        x_pos[1],
        predicted_total,
        bar_width,
        # color=control_color,
    )

    # Add the lift portion on top if positive, or show it as missing if negative
    if percent_lift > 0:
        lift_bar = ax.bar(
            x_pos[1],
            observed_total - predicted_total,
            bar_width,
            bottom=predicted_total,
            # color=lift_color,
            alpha=0.9,
        )
    else:
        # For negative lift, we could show it differently or just adjust the total
        test_total_bar = ax.bar(
            x_pos[1],
            observed_total,
            bar_width,
            # color=control_color,
        )

    # Add dotted line pattern to the top portion (lift)
    if percent_lift > 0:
        # Add hatching pattern to the lift portion
        lift_bar_hatched = ax.bar(
            x_pos[1],
            observed_total - predicted_total,
            bar_width,
            bottom=predicted_total,
            # color=lift_color,
            alpha=0.7,
            edgecolor="white",
            linewidth=1,
            linestyle="--",
        )

    # Customize the plot
    ax.set_xticks(x_pos)
    ax.set_xticklabels(
        ["Control\n(Predicted)", "Test\n(Observed)"],
        fontsize=12,
    )

    # Format y-axis with manual formatting instead of lambda
    # def format_thousands(x, p):
    #     return f'{x:,.0f}'

    # ax.yaxis.set_major_formatter(plt.FuncFormatter(format_thousands))
    ax.set_ylabel(
        f"{value_col.upper()}",
        fontsize=12,
    )

    # Remove top and right spines
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#666666")
    ax.spines["bottom"].set_color("#666666")

    # Add grid
    ax.grid(True, axis="y", alpha=0.3, linestyle="-", linewidth=0.5)
    ax.set_axisbelow(True)

    # Add percent lift annotation
    if percent_lift > 0:
        # Position the annotation in the middle of the lift portion
        annotation_y = predicted_total + (observed_total - predicted_total) / 2
        ax.annotate(
            f"{percent_lift:+.1f}%",
            xy=(x_pos[1], annotation_y),
            xytext=(x_pos[1], annotation_y),
            ha="center",
            va="center",
            fontsize=14,
            color="white",
            bbox=dict(
                boxstyle="round,pad=0.3",
                # facecolor=lift_color,
                alpha=0.8,
                edgecolor="none",
            ),
        )
    else:
        # For negative lift, place annotation above the bar
        ax.annotate(
            f"{percent_lift:+.1f}%",
            xy=(x_pos[1], observed_total),
            xytext=(
                x_pos[1],
                observed_total + max(observed_total, predicted_total) * 0.05,
            ),
            ha="center",
            va="bottom",
            fontsize=14,
            color="red",
            bbox=dict(
                boxstyle="round,pad=0.3", facecolor="white", alpha=0.8, edgecolor="red"
            ),
        )

    # Add value labels on top of bars
    ax.text(
        x_pos[0],
        predicted_total + max(observed_total, predicted_total) * 0.02,
        f"{predicted_total:,.0f}",
        ha="center",
        va="bottom",
        fontsize=11,
    )

    ax.text(
        x_pos[1],
        observed_total + max(observed_total, predicted_total) * 0.02,
        f"{observed_total:,.0f}",
        ha="center",
        va="bottom",
        fontsize=11,
    )

    # Set y-axis limits with some padding
    y_max = max(observed_total, predicted_total) * 1.15
    ax.set_ylim(0, y_max)

    # Add title
    ax.set_title(
        "Test vs Control Comparison",
        fontsize=14,
        pad=20,
    )

    # Adjust layout
    plt.tight_layout()

    return fig
