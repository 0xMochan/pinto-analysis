from typing import NamedTuple

import pandas as pd
import pandera as pa
import streamlit as st
from pandera.typing import DataFrame, Series
from subgrounds import Subgrounds

# PINTO = "https://graph.pinto.money"
PINTOSTALK = "https://graph.pinto.money/pintostalk"
EXCHANGE = "https://graph.pinto.money/exchange"
PROTOCOL = "0xD1A0D188E861ed9d15773a2F3574a2e94134bA8f"
ALL = 100000


class PintoSchema(pa.DataFrameModel):
    datetime: Series[pd.DatetimeTZDtype]
    timestamp: Series[int]
    season: Series[int]
    raining: Series[bool]
    price: Series[float]
    flood_silo_pinto: Series[float]
    flood_field_pinto: Series[float]
    twa_delta_pinto: Series[float]
    delta_pinto: Series[float]
    gm_reward: Series[float]
    twa_minted_pinto: Series[float]
    market_cap: Series[float]
    pod_rate: Series[float]
    temperature: Series[int]
    pod_index: Series[float]
    harvestable_index: Series[float]
    sown_pinto: Series[float]
    harvested_pods: Series[float]
    blocks_to_soil_sold_out: Series[int]
    delta_harvestable_index: Series[float]
    delta_harvestable_pods: Series[float]
    delta_harvested_pods: Series[float]
    delta_issued_soil: Series[float]
    delta_number_of_sowers: Series[int]
    delta_number_of_sows: Series[int]
    delta_pod_index: Series[float]
    delta_pod_rate: Series[float]
    delta_real_rate_of_return: Series[float]
    delta_sown_pinto: Series[float]
    delta_temperature: Series[int]
    delta_unharvestable_pods: Series[float]
    delta_soil: Series[float]
    cum_number_of_sows: Series[int]
    cum_issued_soil: Series[float]
    cum_number_of_sowers: Series[int]
    harvestable_pods: Series[float]
    soil_sold_out: Series[bool]
    soil: Series[float]
    real_rate_of_return: Series[float]
    unharvestable_pods: Series[float]
    cum_pinto_minted: Series[float]
    active_silo_farmers: Series[int]
    delta_active_silo_farmers: Series[int]
    delta_pinto_minted: Series[float]
    delta_grown_stalk_per_season: Series[float]
    delta_germinating_stalk: Series[float]
    delta_deposited_pdv: Series[float]
    delta_unclaimed_stalk: Series[float]
    delta_roots: Series[float]
    delta_stalk: Series[float]
    deposited_pdv: Series[float]
    germinating_stalk: Series[float]
    grown_stalk_per_season: Series[float]
    unclaimed_stalk: Series[float]
    roots: Series[float]
    stalk: Series[float]

    class Config:
        dtype_backend = "pyarrow"


class PlotsSchema(pa.DataFrameModel):
    updated_at: Series[int]
    created_at: Series[int]
    source: Series[str]
    season: Series[int]
    pods: Series[float]
    index: Series[int]
    harvestable_pods: Series[float]
    harvested_pods: Series[float]
    fully_harvested: Series[bool]
    beans_per_pod: Series[float]
    farmer: Series[str]

    class Config:
        dtype_backend = "pyarrow"


class Data(NamedTuple):
    df: DataFrame[PintoSchema]
    plots: DataFrame[PlotsSchema]

    @property
    def latest_season(self):
        return self.df.iloc[-1]


@st.cache_data(ttl="30min", show_spinner="Getting Data..")
def gather_data() -> Data:
    """This function loads the subgraph and queries the data. Subgrounds automatically
    handles the pagination for us.
    """

    with Subgrounds() as sg:
        pintostalk = sg.load_subgraph(PINTOSTALK)
        args = {"first": ALL, "orderBy": "season", "orderDirection": "asc"}
        seasons = pintostalk.Query.seasons(where={"createdAt_gt": 0}, **args)
        fields = pintostalk.Query.fieldHourlySnapshots(
            where={"field": PROTOCOL}, **args
        )
        silos = pintostalk.Query.siloHourlySnapshots(where={"silo": PROTOCOL}, **args)

        plots = pintostalk.Query.plots(
            orderBy="createdAt",
            orderDirection="desc",
            where={"source": "SOW"},
            first=ALL,
        )

        fpath_to_column = [
            (seasons.createdAt, "timestamp"),
            (seasons.season, "season"),
            (seasons.raining, "raining"),
            (seasons.price, "price"),
            (seasons.floodSiloBeans, "flood_silo_pinto"),
            (seasons.floodFieldBeans, "flood_field_pinto"),
            (seasons.deltaB, "twa_delta_pinto"),
            (seasons.deltaBeans, "delta_pinto"),
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
            (plots.id, "id"),
            (plots.updatedAt, "updated_at"),
            (plots.createdAt, "created_at"),
            (plots.harvestAt, "harvest_at"),
            (plots.source, "source"),
            (plots.season, "season"),
            (plots.pods, "pods"),
            (plots.index, "index"),
            (plots.harvestablePods, "harvestable_pods"),
            (plots.harvestedPods, "harvested_pods"),
            (plots.fullyHarvested, "fully_harvested"),
            (plots.beansPerPod, "pinto_spent_per_pod"),
            (plots.farmer.id, "farmer"),
        ]
        fpaths, columns = zip(*fpath_to_column)

        [seasonal_df, silos_df, fields_df, plots_df] = sg.query_df(
            fpaths, columns=columns
        )

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
            "twa_delta_pinto",
            "delta_pinto",
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

        # createdAt -> timestamp
        merged_df["datetime"] = pd.to_datetime(merged_df["timestamp"], unit="s")

        # plots stuff
        plots_df = plots_df.convert_dtypes(dtype_backend="pyarrow")
        plots_df["updated_at"] = pd.to_datetime(plots_df["updated_at"], unit="s")
        plots_df["created_at"] = pd.to_datetime(plots_df["created_at"], unit="s")
        plots_df["harvest_at"] = pd.to_datetime(plots_df["harvest_at"], unit="s")

        # apply decimals to specific columns
        for column in [
            "pods",
            "pinto_spent_per_pod",
            "index",
            "harvestable_pods",
            "harvested_pods",
        ]:
            plots_df[column] /= 10**6

        # st.write(merged_df.dtypes)
        return Data(merged_df, plots_df)
