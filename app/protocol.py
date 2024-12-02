"""
General protocol-level analytics (should match / follow analytics in the data section of
 the pinto.money website).
"""

import streamlit as st
from data import gather_data
from millify import millify
from utils import M as M
from utils import metrics


def main():
    df, latest_season = gather_data()

    st.title("🏗️ Protocol Overview")
    st.subheader("Latest Season")
    metrics(
        M("Price", f"${latest_season['price']:.6f}"),
        M("Marketcap", "${}".format(millify(latest_season["market_cap"], 2))),
        # M("Liquidity", "${}".format(millify(latest_season["market_cap"], 2))),
    )
    metrics(
        M("Season", latest_season["season"]),
        M("Raining", latest_season["raining"]),
        # M("Price", f"${latest_season['price']:.6f}"),
        M("Flood Silo Pinto", millify(latest_season["flood_silo_pinto"], 2)),
    )
    metrics(
        M("Flood Field Pinto", millify(latest_season["flood_field_pinto"], 2)),
        M("Delta P", millify(latest_season["delta_p"], 2)),
        M("Delta Supply", millify(latest_season["delta_supply"], 2)),
        M("GM Reward", millify(latest_season["gm_reward"], 2)),
    )
    metrics(
        M("TWA Minted Pinto", millify(latest_season["twa_minted_pinto"], 2)),
        M("Market Cap", "${}".format(millify(latest_season["market_cap"], 2))),
        M("Cum Pinto Minted", millify(latest_season["cum_pinto_minted"], 2)),
        M("Active Silo Farmers", latest_season["active_silo_farmers"]),
    )
    metrics(
        M("Delta Active Silo Farmers", latest_season["delta_active_silo_farmers"]),
        M("Delta Pinto Minted", millify(latest_season["delta_pinto_minted"], 2)),
        M(
            "Delta Grown Stalk Per Season",
            millify(latest_season["delta_grown_stalk_per_season"], 2),
        ),
        M(
            "Delta Germinating Stalk",
            millify(latest_season["delta_germinating_stalk"], 2),
        ),
    )
    metrics(
        M("Delta Deposited PDV", millify(latest_season["delta_deposited_pdv"], 2)),
        M("Delta Unclaimed Stalk", millify(latest_season["delta_unclaimed_stalk"], 2)),
        M("Delta Roots", millify(latest_season["delta_roots"], 2)),
        M("Delta Stalk", millify(latest_season["delta_stalk"], 2)),
    )
    metrics(
        M("Deposited PDV", millify(latest_season["deposited_pdv"], 2)),
        M("Germinating Stalk", millify(latest_season["germinating_stalk"], 2)),
        M(
            "Grown Stalk Per Season",
            millify(latest_season["grown_stalk_per_season"], 2),
        ),
        M("Unclaimed Stalk", millify(latest_season["unclaimed_stalk"], 2)),
    )
    metrics(
        M("Roots", millify(latest_season["roots"], 2)),
        M("Stalk", millify(latest_season["stalk"], 2)),
    )
    metrics(
        M("Pod Rate", "{}%".format(millify(latest_season["pod_rate"] * 100, 2))),
        M("Temperature", latest_season["temperature"]),
        M("Pod Index", millify(latest_season["pod_index"], 2)),
        M("Harvestable Index", millify(latest_season["harvestable_index"], 2)),
    )
    metrics(
        M("Sown Pinto", millify(latest_season["sown_pinto"], 2)),
        M("Harvested Pods", millify(latest_season["harvested_pods"], 2)),
        M(
            "Blocks to Soil Sold Out",
            latest_season["blocks_to_soil_sold_out"]
            if not latest_season.isna()["blocks_to_soil_sold_out"]
            else "N/A",
        ),
        M(
            "Delta Harvestable Index",
            millify(latest_season["delta_harvestable_index"], 2),
        ),
    )
    metrics(
        M(
            "Delta Harvestable Pods",
            millify(latest_season["delta_harvestable_pods"], 2),
        ),
        M("Delta Harvested Pods", millify(latest_season["delta_harvested_pods"], 2)),
        M("Delta Issued Soil", millify(latest_season["delta_issued_soil"], 2)),
        M("Delta Number of Sowers", latest_season["delta_number_of_sowers"]),
    )
    metrics(
        M("Delta Number of Sows", latest_season["delta_number_of_sows"]),
        M("Delta Pod Index", millify(latest_season["delta_pod_index"], 2)),
        M(
            "Delta Pod Rate",
            "{}%".format(millify(latest_season["delta_pod_rate"] * 100, 2)),
        ),
        M(
            "Delta Real Rate of Return",
            "{}%".format(millify(latest_season["delta_real_rate_of_return"] * 100, 2)),
        ),
    )
    metrics(
        M("Delta Sown Pinto", millify(latest_season["delta_sown_pinto"], 2)),
        M("Delta Temperature", latest_season["delta_temperature"]),
        M(
            "Delta Unharvestable Pods",
            millify(latest_season["delta_unharvestable_pods"], 2),
        ),
        M("Delta Soil", millify(latest_season["delta_soil"], 2)),
    )
    metrics(
        M("Cumulative Number of Sows", latest_season["cum_number_of_sows"]),
        M("Cumulative Issued Soil", millify(latest_season["cum_issued_soil"], 2)),
        M("Cumulative Number of Sowers", latest_season["cum_number_of_sowers"]),
    )

    # trace1 = go.Scatter(x=x, y=y1, mode='lines', name='Delta B', line=dict(color='green'))
    # trace2 = go.Scatter(x=x, y=y2, mode='lines', name='Market Cap and Price', line=dict(color='blue'), yaxis='y2')

    # # Create layout
    # layout = go.Layout(
    #     title='Data Parameters vs Season',
    #     xaxis=dict(title='Season'),
    #     yaxis=dict(title='Delta Beans, Delta B, Reward Beans'),
    #     yaxis2=dict(title='Market Cap and Price', overlaying='y', side='right'),
    #     plot_bgcolor='white'
    # )

    # # Create figure
    # fig = go.Figure(data=[trace1, trace2], layout=layout)
    # st.plotly_chart(fig)


main()
