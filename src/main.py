import asyncio

import pandas as pd
from subgrounds import AsyncSubgrounds

import ui

# PINTO = "https://graph.pinto.money"
PINTOSTALK = "https://graph.pinto.money/pintostalk"


def calculate_flood_details(df: pd.DataFrame) -> pd.DataFrame:
    """This function chunks and aggregates the seasons data into floods."""

    # Convert to millions
    df["flood_silo_pinto"] /= 10**6
    df["flood_field_pinto"] /= 10**6
    df["delta_p"] /= 10**6

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
            # We mostly want a list of all the dps to chart later
            "delta_p": lambda dp: list(dp),
        }
    )

    # helpful total flood calculation
    aggregated_chunks["total_flood_pinto"] = (
        aggregated_chunks["flood_silo_pinto"] + aggregated_chunks["flood_field_pinto"]
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


async def gather_data(subgraph: str) -> pd.DataFrame:
    """This function loads the subgraph and queries the data. Subgrounds automatically
    handles the pagination for us.

    TODO: replace 100000 with ALL when subgrounds supports it.
    """

    async with AsyncSubgrounds() as sg:
        pintostalk = await sg.load_subgraph(subgraph)
        seasons = pintostalk.Query.seasons(
            first=100000, orderBy="season", orderDirection="asc"
        )

        # the subgraph still uses `beans` naming so we convert to `pinto`
        return await sg.query_df(
            [
                seasons.season,
                seasons.raining,
                seasons.price,
                seasons.floodSiloBeans,
                seasons.floodFieldBeans,
                seasons.deltaB,
            ],
            columns=[
                "season",
                "raining",
                "price",
                "flood_silo_pinto",
                "flood_field_pinto",
                "delta_p",
            ],
        )


async def main():
    """This drives the entire streamlit application"""

    df = await gather_data(PINTOSTALK)
    flood_data = calculate_flood_details(df)

    ui.main(df, flood_data)


if __name__ == "__main__":
    asyncio.run(main())
