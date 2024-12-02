"""
This page calculates analytics related to the field, the credit facility for Pinto
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from data import PINTOSTALK, calculate_flood_details, gather_data
from millify import millify
from utils import M, metrics


@st.cache_data(ttl="30min", show_spinner="Getting Data..")
def get_data():
    df = gather_data(PINTOSTALK)
    flood_data = calculate_flood_details(df)
    return df, flood_data




# def main():
#     metrics(
#         M()
#     )
