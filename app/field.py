"""
This page calculates analytics related to the field, the credit facility for Pinto
"""

import altair as alt
import pandas as pd
import streamlit as st
from data import Data, gather_data
from millify import millify
from utils import M, metrics

SECONDS_TO_DAYS = 60 * 60 * 24


def time_to_harvest(data: Data):
    st.title("🌾 Time to Harvest")
    df, plots = data

    def _calc(filtered: pd.DataFrame):
        harvested = filtered[~filtered["harvest_at"].isnull()].copy()
        if harvested.empty:
            st.write("No pods have been harvested in this time period")
            return

        harvested["diff"] = harvested["harvest_at"] - harvested["created_at"]
        metrics(
            M(
                "Total Pods",
                millify((harvested["pods"]).sum(), 2),
            ),
            M(
                "Total Pods Harvestable",
                millify(
                    harvested["harvested_pods"].sum()
                    - harvested["harvestable_pods"].sum(),
                    2,
                ),
            ),
            M(
                "Average (days)",
                millify(
                    harvested["diff"].dt.total_seconds().mean() / SECONDS_TO_DAYS, 1
                ),
            ),
            M(
                "Median (days)",
                millify(
                    harvested["diff"].dt.total_seconds().median() / SECONDS_TO_DAYS, 1
                ),
            ),
        )

        # harvested["diff_days"] = harvested["diff"].dt.total_seconds() / SECONDS_TO_DAYS
        # st.altair_chart(
        #     alt.Chart(harvested)
        #     .mark_bar()
        #     .encode(
        #         x=alt.X("id:N", axis=alt.Axis(labels=False, ticks=False)),
        #         y=alt.Y("diff_days:Q", title="Time to Harvest (days)"),
        #         color=alt.value("#72be95"),
        #     ),
        #     use_container_width=True,
        # )
        filtered["harvest_at"].fillna(pd.Timestamp.now(), inplace=True)
        chart = (
            alt.Chart(filtered)
            .encode(
                x=alt.X("created_at:T", title="Created At"),
                y=alt.Y("rank:O", axis=None),
            )
            .transform_window(
                window=[{"op": "rank", "as": "rank"}],
                sort=[{"field": "created_at", "order": "ascending"}],
            )
            .transform_filter((alt.datum.rank <= 50))
        )
        line = chart.mark_rule(color="#db646f").encode(
            x="created_at:T", x2="harvest_at:T", y=alt.Y("rank:O", axis=None)
        )
        points = chart.mark_point(size=100, opacity=1, filled=True).encode(
            x=alt.X("created_at:T", title="Created At"),
            y=alt.Y("rank:O", axis=None),
            color=alt.Color("harvest_at:T"),
        )

        harvest_points = (
            chart.mark_point(size=100, opacity=1, filled=True)
            .encode(
                x=alt.X("harvest_at:T", title="Harvest At"),
                y=alt.Y("rank:O", axis=None),
                color=alt.Color("harvest_at:T"),
            )
            .transform_filter(alt.datum.fully_harvested == True)  # noqa
        )
        st.altair_chart(
            alt.layer(line, points, harvest_points)
            .configure_legend(disable=True)
            .interactive(),
            use_container_width=True,
        )

    all, month, week, day = st.tabs(["All", "30d", "7d", "24hr"])

    with all:
        _calc(plots)

    with day:
        _calc(plots[plots["created_at"] > pd.Timestamp.now() - pd.Timedelta(days=1)])

    with week:
        _calc(plots[plots["created_at"] > pd.Timestamp.now() - pd.Timedelta(days=7)])

    with month:
        _calc(plots[plots["created_at"] > pd.Timestamp.now() - pd.Timedelta(days=30)])


def max_temperature_graph(df: pd.DataFrame):
    df["temperature"] /= 100
    nearest = alt.selection_point(
        nearest=True,
        on="pointerover",
        fields=["season"],
        empty=True,
    )

    line = (
        alt.Chart(df)
        .mark_line(color="#72be95")
        .encode(
            x=alt.X("season", title="Season", axis=alt.Axis(grid=False, tickCount=5)),
            y=alt.Y(
                "temperature",
                title="Max Temperature",
                axis=alt.Axis(grid=True, tickCount=3, format="%"),
            ),
        )
    )

    selectors = (
        alt.Chart(df)
        .mark_point()
        .encode(
            x="season:Q",
            opacity=alt.value(0),
            tooltip=[
                {"field": "season", "type": "quantitative", "title": "Season"},
                {
                    "field": "temperature",
                    "type": "quantitative",
                    "title": "Max Temperature",
                    "format": ".0%",
                },
            ],
        )
        .add_params(nearest)
    )

    when_near = alt.when(nearest)

    # Draw points on the line, and highlight based on selection
    points = line.mark_point().encode(
        opacity=when_near.then(alt.value(1)).otherwise(alt.value(0))
    )

    rules = (
        alt.Chart(df)
        .mark_rule(color="gray")
        .encode(
            x="season:Q",
        )
        .transform_filter(nearest)
    )

    chart = alt.layer(line, selectors, points, rules).properties(
        title="Max temperature over time"
    )

    st.altair_chart(chart.interactive(bind_y=False), use_container_width=True)


def main():
    data = gather_data()
    st.header("🌾 Field Analytics")
    st.subheader("Season {}".format(data.latest_season["season"]))

    # quick metrics
    metrics(
        M(
            "Max Temperature",
            "{}%".format(int(data.latest_season["temperature"])),
            "{}%".format(int(data.latest_season["delta_temperature"])),
        ),
        M(
            "Available Soil",
            millify(data.latest_season["soil"], 2),
            millify(data.latest_season["delta_soil"], 2),
        ),
        M(
            "Pod Line",
            millify(data.latest_season["unharvestable_pods"], 2),
            millify(data.latest_season["delta_unharvestable_pods"], 2),
        ),
    )

    metrics(
        M(
            "Total Sown Pinto",
            millify(data.latest_season["sown_pinto"]),
            millify(data.latest_season["delta_sown_pinto"]),
        ),
        M(
            "Total Harvested/Harvestable Pods",
            millify(
                data.latest_season["harvested_pods"]
                + data.latest_season["harvestable_pods"]
            ),
            millify(
                data.latest_season["delta_harvested_pods"]
                + data.latest_season["delta_harvestable_pods"]
            ),
        ),
        M(
            "Pods Awaiting Harvest",
            millify(data.latest_season["harvestable_pods"]),
            millify(data.latest_season["delta_harvestable_pods"]),
        ),
    )

    max_temperature_graph(data.df)
    time_to_harvest(data)


main()
