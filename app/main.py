import streamlit as st
from st_copy_to_clipboard import st_copy_to_clipboard

from data import gather_data



def disclaimers():
    with st.popover("Disclaimers", use_container_width=True):
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

    st.set_page_config(
        page_title="Entrypoint",
        page_icon="🫘",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            "Get Help": "https://pinto.money/discord",
            "Report a bug": "https://github.com/0xMochan/pinto-analysis/issues",
            "About": "This app showcases some data analysis on the Pinto Protocol",
        },
    )

    _, latest_season = gather_data()

    with st.sidebar:
        left, right = st.columns(2, vertical_alignment="center")
        with left:
            disclaimers()
        right.button(
            "Refresh Data", on_click=st.cache_data.clear, use_container_width=True
        )
        st.divider()
        st.markdown("🌱 **Current Season** ・ {}".format(int(latest_season["season"])))
        st.markdown(
            "🏷️ **Latest Price** ・ ${:.6f}".format(float(latest_season["price"]))
        )
        st.divider()
        st.subheader("App Links")
        st.markdown("- [Github](https://github.com/0xMochan/pinto-analysis)\n")
        st.divider()
        st.subheader("Pinto Links")
        st.markdown(
            "- [Protocol](https://pinto.money)\n"
            "- [Docs](https://docs.pinto.money)\n"
            "- [Github](https://github.com/pinto-org/protocol)\n"
            "- [Discord](https://pinto.money/discord)"
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
    st.navigation(
        {
            "Data Apps": [
                st.Page("protocol.py", title="🏗️ Protocol Overview"),
                st.Page("flood.py", title="🌊 Flood Analytics"),
            ]
        }
    ).run()
