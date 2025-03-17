"""
This page analyzes the seasonal data, chunking it by floods to determine the performance
 of floods on the Pinto Protocol.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from data import gather_data
from millify import millify
from utils import M, metrics


def calculate_flood_details(df: pd.DataFrame) -> pd.DataFrame:
    """This function chunks and aggregates the seasons data into floods."""

    # helpful total flood calculation
    df["total_flood_pinto"] = df["flood_silo_pinto"] + df["flood_field_pinto"]

    # We shift raining over to detect differences between raining regions
    df["raining"] = df["raining"].astype(int)
    df["flood_no"] = (df["raining"] != df["raining"].shift()).cumsum()
    df["flood_length"] = 0

    raining_chunks = df[df["raining"] == 1].groupby("flood_no")

    # we aggregate based on specific functions for each field
    aggregated_chunks = raining_chunks.agg(
        {
            "season": "first",
            "flood_length": "size",
            "price": "mean",
            "flood_silo_pinto": "sum",
            "flood_field_pinto": "sum",
            "total_flood_pinto": "sum",
            "delta_pinto": "sum",
            "gm_reward": "sum",
            "twa_minted_pinto": "sum",
        }
    )

    # drop aggregated chunks with less than 2 seasons
    aggregated_chunks = aggregated_chunks[aggregated_chunks["flood_length"] > 1]

    # we re-index the dataframe to start from 1
    aggregated_chunks.reset_index(drop=True, inplace=True)
    aggregated_chunks.index = aggregated_chunks.index + 1

    # remove one from flood length to not include the raining season
    aggregated_chunks["flood_length"] -= 1

    aggregated_chunks.rename(
        columns={
            "season": "raining_season",
            "price": "average_price",
        },
        inplace=True,
    )
    return aggregated_chunks


def is_raining(df: pd.DataFrame) -> bool:
    return df.iloc[-1]["raining"] == 1


def general_flood_data(df: pd.DataFrame, flood_data: pd.DataFrame):
    st.subheader("⚙ General Flood Data")

    metrics(
        M(
            "Average Flood Length (in Seasons)",
            millify(flood_data["flood_length"].mean(), 1),
        ),
        M(
            "Median Flood Length (in Seasons)",
            millify(flood_data["flood_length"].median(), 1),
        ),
        M(
            "Total Number of Floods",
            millify(len(flood_data)),
        ),
    )

    metrics(
        M(
            "Total Pinto sold to Silo",
            millify(flood_data["flood_silo_pinto"].sum(), 2),
        ),
        M(
            "Total Pinto sold to Field",
            millify(flood_data["flood_field_pinto"].sum(), 2),
        ),
        M(
            "Total Pinto minted and sold",
            millify(flood_data["total_flood_pinto"].sum(), 2),
        ),
    )

    plot, data = st.tabs(["Plot", "Data"])

    with plot:
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=flood_data.index,
                y=flood_data["flood_silo_pinto"],
                name="Silo",
                marker_color="rgba(70, 130, 180, 0.75)",
            )
        )
        fig.add_trace(
            go.Bar(
                x=flood_data.index,
                y=flood_data["flood_field_pinto"],
                name="Field",
                marker_color="rgba(34, 139, 34, 0.75)",
            )
        )
        if is_raining(df):
            text = "Current Flood: {} Pinto Sold".format(
                millify(flood_data["total_flood_pinto"].iloc[-1], 2)
            )
        else:
            text = "Last Flood: {} Pinto Sold".format(
                millify(flood_data["total_flood_pinto"].iloc[-1], 2)
            )
        fig.add_annotation(
            x=len(flood_data["total_flood_pinto"]),
            y=flood_data["total_flood_pinto"].iloc[-1],
            text=text,
            showarrow=True,
            bgcolor="rgba(70, 130, 180, 0.25)",
            arrowcolor="rgba(70, 130, 180, 0.75)",
            arrowsize=0.5,
            bordercolor="black",
            borderwidth=2,
            borderpad=4,
        )
        fig.update_layout(barmode="stack")
        fig.update_xaxes(title_text="Flood Index")
        fig.update_yaxes(title_text="Pinto (Millions)")
        fig.update_layout(title="Pinto sold to Silo and Field")
        st.plotly_chart(fig)

    with data:
        to_display = flood_data.copy()
        format = "{:,.1f}".format
        to_display["flood_silo_pinto"] = to_display["flood_silo_pinto"].map(format)
        to_display["flood_field_pinto"] = to_display["flood_field_pinto"].map(format)
        to_display["total_flood_pinto"] = to_display["total_flood_pinto"].map(format)

        to_display = to_display.rename(
            columns={
                "raining_season": "Raining Season",
                "average_price": "Average Price",
                "flood_silo_pinto": "Sold to Silo",
                "flood_field_pinto": "Sold to Field",
                "flood_length": "Number of Seasons",
                "total_flood_pinto": "Total Pinto Sold",
                "twa_delta_pinto": "Time Weighted Delta Pinto",
            },
        )[::-1]

        if is_raining(df):
            to_display = to_display.style.apply(
                lambda x: [
                    "background-color: rgba(70, 130, 180, 0.25)"
                    if x.name == len(flood_data)
                    else ""
                    for _ in x
                ],
                axis=1,
            )

        st.dataframe(to_display)


def current_flood(df: pd.DataFrame, flood_data: pd.DataFrame):
    if is_raining(df):
        st.subheader("🌧️ Currently Flooding")
    else:
        last_flood_season = int(df[df["raining"] == 1].iloc[-1]["season"])
        seasons_ago = int(df.iloc[-1]["season"] - last_flood_season)
        st.subheader(f"🌱 Last flood was {seasons_ago} seasons ago")

    flood_index = st.number_input(
        "Flood Number",
        min_value=1,
        max_value=len(flood_data),
        value=len(flood_data),
    )

    # select current flood from selected index
    flood_index -= 1
    current_flood = flood_data.iloc[flood_index]
    end_season = int(current_flood["raining_season"] + current_flood["flood_length"])
    seasons_during_flood = df[
        (df["season"] >= current_flood["raining_season"]) & (df["season"] <= end_season)
    ]

    # if chosen flood is not the earliest flood, calculate deltas
    if flood_index - 1 >= 0:
        last_flood = flood_data.iloc[flood_index - 1]
        length_delta = int(current_flood["flood_length"] - last_flood["flood_length"])
        pinto_silo_delta = millify(
            current_flood["flood_silo_pinto"] - last_flood["flood_silo_pinto"], 2
        )
        pinto_field_delta = millify(
            current_flood["flood_field_pinto"] - last_flood["flood_field_pinto"], 2
        )
        pinto_total_delta = millify(
            current_flood["total_flood_pinto"] - last_flood["total_flood_pinto"], 2
        )
        previous_flood_raining_season = int(last_flood["raining_season"])

    # if chosen flood is the earliest flood, set deltas to None
    else:
        length_delta = None
        pinto_silo_delta = None
        pinto_field_delta = None
        pinto_total_delta = None
        previous_flood_raining_season = None

    raining_season = int(current_flood["raining_season"])
    flood_length = int(current_flood["flood_length"])
    metrics(
        M(
            "Rainy Season",
            raining_season,
            previous_flood_raining_season,
        ),
        M(
            "Length of Flood",
            int(current_flood["flood_length"]),
            length_delta,
        ),
        M(
            "Flooding Seasons",
            (
                (
                    f"{raining_season+1}-{end_season}"
                    if flood_length > 1
                    else raining_season + 1
                )
                if not (flood_index + 1 == len(flood_data) and is_raining(df))
                else f"{raining_season+1}-"
            ),
        ),
    )

    metrics(
        M(
            "Total Pinto sold to Silo",
            millify(current_flood["flood_silo_pinto"], 2),
            pinto_silo_delta,
        ),
        M(
            "Total Pinto sold to Field",
            millify(current_flood["flood_field_pinto"], 2),
            pinto_field_delta,
        ),
        M(
            "Total Pinto minted and sold",
            millify(current_flood["total_flood_pinto"], 2),
            pinto_total_delta,
        ),
    )

    plot, data = st.tabs(["Plot", "Data"])

    with plot:
        # line plot for all pinto stats during flood seasons
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=seasons_during_flood["season"],
                y=seasons_during_flood["twa_minted_pinto"],
                mode="lines+markers",
                name="TWA Minted Pinto",
                marker=dict(color="rgba(34, 139, 34, 0.75)"),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=seasons_during_flood["season"],
                y=seasons_during_flood["twa_delta_pinto"],
                mode="lines+markers",
                name="TWAΔP",
                marker=dict(color="rgba(70, 130, 180, 0.75)"),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=seasons_during_flood["season"],
                y=seasons_during_flood["total_flood_pinto"],
                mode="lines+markers",
                name="Minted Flood Pinto",
                marker=dict(color="rgba(255, 99, 71, 0.75)"),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=seasons_during_flood["season"],
                y=seasons_during_flood["gm_reward"],
                mode="lines",
                name="gm() Reward",
                marker=dict(color="rgba(255, 215, 0, 0.75)"),
            )
        )
        annotation = (
            "TWAΔP: <span style='color:#90EE90'>{}</span><br>"
            "<span style='color:gray'>Season {}</span>"
        )
        latest_flood_season = seasons_during_flood.iloc[-1]
        fig.add_annotation(
            x=current_flood["raining_season"] + current_flood["flood_length"],
            y=latest_flood_season["twa_delta_pinto"],
            text=annotation.format(
                millify(latest_flood_season["twa_delta_pinto"], 2),
                int(current_flood["raining_season"] + current_flood["flood_length"]),
            ),
            showarrow=False,
            bgcolor="rgba(0, 0, 139, 0.20)",
            bordercolor="black",
            borderwidth=0,
            borderpad=4,
            yshift=-45,
        )
        fig.add_annotation(
            x=current_flood["raining_season"],
            y=max(
                seasons_during_flood[
                    [
                        "twa_delta_pinto",
                        "twa_minted_pinto",
                        "total_flood_pinto",
                        "gm_reward",
                    ]
                ].max()
            ),
            text="Raining Season",
            showarrow=False,
            ax=0,
            ay=-40,
            bgcolor="rgba(255, 215, 0, 0.25)",
            bordercolor="black",
            borderwidth=1,
            borderpad=4,
            yshift=20,
        )
        fig.update_xaxes(title_text="Seasons")
        fig.update_yaxes(title_text="Pinto")
        fig.update_layout(title="Pinto Stats during Flood Seasons")

        st.plotly_chart(fig)

        # bar plot for all delta pinto introduced during flood seasons
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=seasons_during_flood["season"],
                y=seasons_during_flood["delta_pinto"],
                name="Instantaneous Delta Pinto",
            )
        )
        fig.update_xaxes(title_text="Seasons")
        fig.update_yaxes(title_text="Pintos")
        fig.update_layout(title="Pintos Minted during Flood Seasons")

        selected = st.plotly_chart(
            fig, on_select="rerun", selection_mode=["lasso", "points", "box"]
        )
        if points := selected["selection"]["point_indices"]:
            t0 = int(points[0] + current_flood["raining_season"])
            t1 = int(points[-1] + current_flood["raining_season"])
            summed = seasons_during_flood.iloc[points]["delta_pinto"].sum()
            with st.expander(
                f"{summed:,.2f} Pinto distributed during Selected Season(s) {t0}-{t1}"
            ):
                for point in points:
                    season = seasons_during_flood.iloc[point]
                    # pie chart of pinto distribution during selected season
                    pie_data = pd.DataFrame(
                        {
                            "Category": [
                                "Sold to Silo",
                                "Sold to Field",
                                "TWA Minted Pinto",
                                "gm() Reward",
                            ],
                            "Values": [
                                season["flood_silo_pinto"],
                                season["flood_field_pinto"],
                                season["twa_minted_pinto"],
                                season["gm_reward"],
                            ],
                        }
                    )
                    fig = px.pie(
                        pie_data,
                        values="Values",
                        names="Category",
                        title=f"{season['delta_pinto']: ,.2f} Pinto distributed during Season {int(season['season'])}",
                    )
                    st.plotly_chart(fig)

    with data:
        to_display = seasons_during_flood[
            [
                "season",
                "price",
                "flood_silo_pinto",
                "flood_field_pinto",
                "total_flood_pinto",
                "twa_delta_pinto",
                "gm_reward",
                "delta_pinto",
            ]
        ].copy()
        format = "{:,.1f}".format
        columns_to_format = [
            "flood_silo_pinto",
            "flood_field_pinto",
            "total_flood_pinto",
            "twa_delta_pinto",
            "gm_reward",
            "delta_pinto",
        ]
        to_display[columns_to_format] = to_display[columns_to_format].map(format)
        to_display["pod_rate"] = seasons_during_flood["pod_rate"].map("{:.2%}".format)

        to_display = to_display.rename(
            columns={
                "season": "Season",
                "price": "Price",
                "flood_silo_pinto": "Sold to Silo",
                "flood_field_pinto": "Sold to Field",
                "total_flood_pinto": "Total Pinto Sold",
                "twa_delta_pinto": "Time Weighted Average Delta Pinto",
                "gm_reward": "gm() Reward",
                "delta_pinto": "Instantaneous Delta Pinto",
                "twa_minted_pinto": "Time Weighted Average Minted Pinto",
                "pod_rate": "Pod Rate",
            },
        )[::-1]
        st.dataframe(to_display, hide_index=True)


def main():
    st.title("🌊 Flood Inspector")

    st.markdown(
        """
        The protocol manages Pinto supply during periods of high demand through a process called flooding. This process starts when a season's Time Weighted Average (TWA) deltaP is positive and the Pod Rate is above 5%. The first season is the raining season, if it continues, the protocol declares a flood.
        
        During flooding seasons, the protocol mints additional Pinto at the start of each season and sells them to the highest pinto shortage in the silo LP returning excess tokens back to rainstalk holders (flood silo returns). Additionally, up to 0.1% of the pinto supply worth of pods that grew from sown pinto before it began to rain become harvestable (flood field returns).

        This page analyzes the seasonal data to determine the performance of floods on the Pinto Protocol.
        """
    )

    overview, flood_analysis = st.tabs(["Overview", "Flood Analysis"])

    data = gather_data()
    flood_data = calculate_flood_details(data.df)

    with overview:
        general_flood_data(data.df, flood_data)

    with flood_analysis:
        current_flood(data.df, flood_data)


main()
