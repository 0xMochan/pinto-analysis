from typing import NamedTuple

import streamlit as st
from streamlit.elements.metric import Delta, DeltaColor, LabelVisibility, Value


class M(NamedTuple):
    label: str
    value: Value
    delta: Delta = None
    delta_color: DeltaColor = "normal"
    help: str | None = None
    label_visibility: LabelVisibility = "visible"


def metrics(*metrics: M):
    """Display multiple metrics in a row using `st.columns`"""

    columns = st.columns(len(metrics))
    for metric, col in zip(metrics, columns):
        col.metric(*metric)
