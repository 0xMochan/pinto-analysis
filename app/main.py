import streamlit as st
from st_copy_to_clipboard import st_copy_to_clipboard

from data import PINTOSTALK, get_latest_season


@st.cache_data(ttl="30min", show_spinner="Getting Data..")
def get_data():
    return get_latest_season(PINTOSTALK)


def disclaimers():
    with st.popover("Disclaimers"):
        st.warning(
            "This application is for informational purposes only and is not "
            "representative of financial advice. Please do your own research."
        )
        st.warning(
            "This application is in active development and the data may be inaccurate."
        )
        st.warning(
            "Floods only occur when A) a dollar exceeds 1$ after a season and "
            "B) when the pod rate goes above 5%"
            "\n"
            "This application does not consider condition B yet (which has not hit yet)."
        )


def main():
    """This drives the entire streamlit application"""

    latest_season = get_data()

    with st.sidebar:
        st.title("🫘 Pinto Analysis")
        left, right = st.columns(2)
        with left:
            disclaimers()
        right.button("Refresh Data", on_click=st.cache_data.clear)
        st.divider()
        st.markdown("🌱 **Current Season** ・ {}".format(int(latest_season["season"])))
        st.markdown(
            "🏷️ **Current Price** ・ ${:.2f}".format(float(latest_season["price"]))
        )
        st.divider()
        st.subheader("Links")
        st.markdown(
            "- [Pinto Protocol](https://pinto.money)\n"
            "- [Pinto Docs](https://docs.pinto.money)\n"
            "- [Pinto Github](https://github.com/pinto-org/protocol)\n"
            "- [Pinto Discord](https://pinto.money/discord)"
        )
        st.divider()
        st.markdown("*By [0xMochan](https://twitter.com/0xMochan)*")
        st.markdown("Support my work via my EVM-compatible address")
        st.markdown("`0xe23cE0f5dC9D3DA1FD69d3A169F5596F5A5669AA`")
        col1, col2 = st.columns(2)
        with col1:
            st_copy_to_clipboard("0xe23cE0f5dC9D3DA1FD69d3A169F5596F5A5669AA")
        col2.html("<span style='color: grey'>Click to copy to clipboard!</span>")


if __name__ == "__main__":
    main()
    st.navigation({"Data Apps": [st.Page("flood.py", title="🌊 Flood Analysis")]}).run()
