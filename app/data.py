import pandas as pd
import streamlit as st
from subgrounds import Subgrounds

# PINTO = "https://graph.pinto.money"
PINTOSTALK = "https://graph.pinto.money/pintostalk"
EXCHANGE = "https://graph.pinto.money/exchange"
PROTOCOL = "0xD1A0D188E861ed9d15773a2F3574a2e94134bA8f"


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
            "delta_supply": "sum",
            "gm_reward": "sum",
            "twa_minted_pinto": "sum",
        }
    )

    # we re-index the dataframe to start from 1
    aggregated_chunks.reset_index(drop=True, inplace=True)
    aggregated_chunks.index = aggregated_chunks.index + 1

    aggregated_chunks.rename(
        columns={
            "season": "starting_season",
            "price": "average_price",
        },
        inplace=True,
    )
    return aggregated_chunks


@st.cache_data(ttl="30min", show_spinner="Getting Data..")
def gather_data() -> tuple[pd.DataFrame, pd.Series]:
    """This function loads the subgraph and queries the data. Subgrounds automatically
    handles the pagination for us.

    TODO: replace 100000 with ALL when subgrounds supports it.
    """

    with Subgrounds() as sg:
        pintostalk = sg.load_subgraph(PINTOSTALK)
        args = {"first": 100000, "orderBy": "season", "orderDirection": "asc"}
        seasons = pintostalk.Query.seasons(**args)
        fields = pintostalk.Query.fieldHourlySnapshots(
            where={"field": PROTOCOL}, **args
        )
        silos = pintostalk.Query.siloHourlySnapshots(where={"silo": PROTOCOL}, **args)

        fpath_to_column = [
            (seasons.season, "season"),
            (seasons.raining, "raining"),
            (seasons.price, "price"),
            (seasons.floodSiloBeans, "flood_silo_pinto"),
            (seasons.floodFieldBeans, "flood_field_pinto"),
            (seasons.deltaB, "delta_p"),
            (seasons.deltaBeans, "delta_supply"),
            (seasons.incentiveBeans, "gm_reward"),
            (seasons.rewardBeans, "twa_minted_pinto"),
            (seasons.marketCap, "market_cap"),
            (silos.beanMints, "cum_pinto_minted"),
            (silos.activeFarmers, "active_silo_farmers"),
            # (silos.avgGrownStalkPerBdvPerSeason, "avg_grown_stalk_per_bdv"),
            # (silos.beanToMaxLpGpPerBdvRatio, ),
            # (silos.createdAt, ),
            (silos.deltaActiveFarmers, "delta_active_silo_farmers"),
            # (silos.deltaAvgGrownStalkPerBdvPerSeason, ),
            (silos.deltaBeanMints, "delta_pinto_minted"),
            (silos.deltaGrownStalkPerSeason, "delta_grown_stalk_per_season"),
            (silos.deltaGerminatingStalk, "delta_germinating_stalk"),
            (silos.deltaDepositedBDV, "delta_deposited_pdv"),
            (silos.deltaPlantableStalk, "delta_unclaimed_stalk"),
            (silos.deltaRoots, "delta_roots"),
            (silos.deltaStalk, "delta_stalk"),
            (silos.depositedBDV, "deposited_pdv"),
            (silos.germinatingStalk, "germinating_stalk"),
            (silos.grownStalkPerSeason, "grown_stalk_per_season"),
            # (silos.id, ),
            (silos.plantableStalk, "unclaimed_stalk"),
            (silos.season, "silo_season"),
            (silos.roots, "roots"),  # uncompounded stalk
            (silos.stalk, "stalk"),
            # (silos.updatedAt, ),
            # (fields.id, ""),
            (fields.season, "field_season"),
            (fields.podRate, "pod_rate"),
            (fields.temperature, "temperature"),
            (fields.podIndex, "pod_index"),
            (fields.harvestableIndex, "harvestable_index"),
            (fields.sownBeans, "sown_pinto"),
            (fields.harvestedPods, "harvested_pods"),
            # (fields.createdAt, ""),
            # (fields.caseId, ""),
            (fields.blocksToSoldOutSoil, "blocks_to_soil_sold_out"),
            (fields.deltaHarvestableIndex, "delta_harvestable_index"),
            (fields.deltaHarvestablePods, "delta_harvestable_pods"),
            (fields.deltaHarvestedPods, "delta_harvested_pods"),
            (fields.deltaIssuedSoil, "delta_issued_soil"),
            (fields.deltaNumberOfSowers, "delta_number_of_sowers"),
            (fields.deltaNumberOfSows, "delta_number_of_sows"),
            (fields.deltaPodIndex, "delta_pod_index"),
            (fields.deltaPodRate, "delta_pod_rate"),
            (fields.deltaRealRateOfReturn, "delta_real_rate_of_return"),
            (fields.deltaSownBeans, "delta_sown_pinto"),
            (fields.deltaTemperature, "delta_temperature"),
            (fields.deltaUnharvestablePods, "delta_unharvestable_pods"),
            (fields.deltaSoil, "delta_soil"),
            (fields.numberOfSows, "cum_number_of_sows"),
            (fields.issuedSoil, "cum_issued_soil"),
            (fields.numberOfSowers, "cum_number_of_sowers"),
            (fields.harvestablePods, "harvestable_pods"),
            (fields.soilSoldOut, "soil_sold_out"),
            (fields.soil, "soil"),
            (fields.realRateOfReturn, "real_rate_of_return"),
            (fields.unharvestablePods, "unharvestable_pods"),
            # (fields.updatedAt, ""),
        ]
        fpaths, columns = zip(*fpath_to_column)

        [seasonal_df, silos_df, fields_df] = sg.query_df(fpaths, columns=columns)

        # Merge seasonal_df and fields_df on 'season' and 'field_season'
        merged_df = pd.merge(
            seasonal_df,
            fields_df,
            left_on="season",
            right_on="field_season",
            how="left",
        )
        merged_df = pd.merge(
            merged_df, silos_df, left_on="season", right_on="silo_season", how="left"
        )

        merged_df.drop(columns=["field_season", "silo_season"], inplace=True)

        # Convert merged_df to more memory-efficient format
        merged_df = merged_df.apply(
            lambda col: pd.to_numeric(col, errors="coerce")
            if col.dtype == "object"
            else col
        )
        merged_df = merged_df.convert_dtypes(dtype_backend="pyarrow")

        # apply decimals to specific columns
        for column in [
            "flood_silo_pinto",
            "flood_field_pinto",
            "delta_p",
            "delta_supply",
            "gm_reward",
            "twa_minted_pinto",
            "pod_index",
            "harvestable_index",
            "sown_pinto",
            "harvested_pods",
            "delta_harvestable_index",
            "delta_harvestable_pods",
            "delta_harvested_pods",
            "delta_issued_soil",
            "delta_pod_index",
            "delta_sown_pinto",
            "delta_unharvestable_pods",
            "delta_soil",
            "cum_issued_soil",
            "harvestable_pods",
            "soil",
            "unharvestable_pods",
            "cum_pinto_minted",
            "delta_pinto_minted",
            "delta_grown_stalk_per_season",
            "delta_germinating_stalk",
            "delta_deposited_pdv",
            "delta_unclaimed_stalk",
            "delta_stalk",
            "deposited_pdv",
            "germinating_stalk",
            "grown_stalk_per_season",
            "unclaimed_stalk",
            "stalk",
            "roots",
            "delta_roots",
        ]:
            merged_df[column] /= 10**6

        return merged_df, merged_df.iloc[-1]
