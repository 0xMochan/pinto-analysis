import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from millify import millify


def is_raining(df: pd.DataFrame) -> bool:
    return df.iloc[-1]["raining"] == 1


def general_flood_data(df: pd.DataFrame, flood_data: pd.DataFrame):
    st.subheader("⚙ General Flood Data")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Number of Floods", millify(len(flood_data)))
    col2.metric(
        "Average Flood Length (in Seasons)",
        millify(flood_data["flood_length"].mean(), 1),
    )
    col3.metric(
        "Median Flood Length (in Seasons)",
        millify(flood_data["flood_length"].median(), 1),
    )

    col1, col2, col3 = st.columns(3)
    col1.metric(
        "Total Pinto sold to Silo",
        millify(flood_data["flood_silo_pinto"].sum(), 2),
    )
    col2.metric(
        "Total Pinto sold to Field",
        millify(flood_data["flood_field_pinto"].sum(), 2),
    )
    col3.metric(
        "Total Pinto minted and sold",
        millify(
            flood_data["total_flood_pinto"].sum(),
            2,
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
            )
        )
        fig.add_trace(
            go.Bar(
                x=flood_data.index,
                y=flood_data["flood_field_pinto"],
                name="Field",
            )
        )
        fig.add_annotation(
            x=len(flood_data["total_flood_pinto"]),
            y=flood_data["total_flood_pinto"].iloc[-1],
            text="Current Flood: {} Pinto Sold".format(
                millify(flood_data["total_flood_pinto"].iloc[-1], 2)
            ),
            showarrow=True,
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
                "starting_season": "Starting Season",
                "average_price": "Average Price",
                "flood_silo_pinto": "Sold to Silo",
                "flood_field_pinto": "Sold to Field",
                "flood_length": "Number of Seasons",
                "total_flood_pinto": "Total Pinto Sold",
                "delta_p": "Time Weighted Delta Pinto",
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
        st.subheader("🌊 Currently Flooding")
    else:
        last_flood_season = int(df[df["raining"] == 1].iloc[0]["season"])
        st.subheader(f"🌱 Last Flood during season {last_flood_season}")

    flood_index = st.number_input(
        "Flood Number",
        min_value=1,
        max_value=len(flood_data),
        value=len(flood_data),
    )

    # select current flood from selected index
    flood_index -= 1
    current_flood = flood_data.iloc[flood_index]

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
        previous_flood_starting_season = int(last_flood["starting_season"])

    # if chosen flood is the earliest flood, set deltas to None
    else:
        length_delta = None
        pinto_silo_delta = None
        pinto_field_delta = None
        pinto_total_delta = None
        previous_flood_starting_season = None

    col1, col2, col3 = st.columns(3)
    col1.metric(
        "Starting Season",
        int(current_flood["starting_season"]),
        previous_flood_starting_season,
    )
    col2.metric(
        "Length of Flood",
        int(current_flood["flood_length"]),
        length_delta,
    )
    if is_raining(df):
        col3.metric(
            "Current Season",
            int(current_flood["starting_season"] + current_flood["flood_length"] - 1),
        )
    else:
        col3.metric(
            "End Season",
            int(current_flood["starting_season"] + current_flood["flood_length"] - 1),
        )

    col1, col2, col3 = st.columns(3)
    col1.metric(
        "Total Pinto sold to Silo",
        millify(current_flood["flood_silo_pinto"], 2),
        pinto_silo_delta,
    )
    col2.metric(
        "Total Pinto sold to Field",
        millify(current_flood["flood_field_pinto"], 2),
        pinto_field_delta,
    )
    col3.metric(
        "Total Pinto minted and sold",
        millify(current_flood["total_flood_pinto"], 2),
        pinto_total_delta,
    )

    # graphing delta_ps for the current flood
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=list(
                i + current_flood["starting_season"]
                for i in range(len(current_flood["delta_p"]))
            ),
            y=current_flood["delta_p"],
            mode="lines",
            name="Delta P",
        )
    )
    annotation = "Latest Delta P: <span style='color:#90EE90'>{}</span><br><span style='color:gray'>Season {}</span>"
    fig.add_annotation(
        x=current_flood["starting_season"] + current_flood["flood_length"] - 1,
        y=current_flood["delta_p"][-1],
        text=annotation.format(
            millify(current_flood["delta_p"][-1], 2),
            current_flood["starting_season"] + current_flood["flood_length"] - 1,
        ),
        showarrow=True,
    )
    fig.update_xaxes(title_text="Seasons")
    fig.update_yaxes(title_text="Delta Pintos")
    fig.update_layout(title="Time Weighted Delta Pinto for Current Flood")
    st.plotly_chart(fig)


def main(df: pd.DataFrame, flood_data: pd.DataFrame):
    st.title("🫘 Pinto Flood Analysis")

    with st.popover("Disclaimers"):
        st.warning(
            "This application is for informational purposes only and is not financial advice."
        )
        st.warning(
            "Floods only occur when A) a dollar exceeds 1$ after a season and "
            "B) when the pod rate goes above 5%"
            "\n"
            "This application does not consider condition B yet (which has not hit yet)."
        )

    st.markdown(
        "This app conducts preliminary analysis on flood data from the "
        "[pinto.money](https://pinto.money) protocol. The data is sourced from the "
        "[Pintostalk subgraph](https://graph.pinto.money/explorer/pintostalk) and uses "
        "[subgrounds](https://github.com/0xPlaygrounds/subgrounds) for data manipulation."
    )

    overview, flood_analysis = st.tabs(["Overview", "Flood Analysis"])

    with overview:
        general_flood_data(df, flood_data)

    with flood_analysis:
        current_flood(df, flood_data)
