import streamlit as st


def main():
    st.markdown(
        "This app conducts various analytics on the [Pinto Protocol](https://pinto.money)."
    )
    st.markdown(
        "The data is sourced from the "
        "[Pintostalk subgraph](https://graph.pinto.money/explorer/pintostalk) and uses "
        "[subgrounds](https://github.com/0xPlaygrounds/subgrounds) for data manipulation."
    )
    st.divider()
    st.subheader("Links")
    st.markdown("- [Github](https://github.com/0xMochan/pinto-analysis)\n")
    st.subheader("Pinto Links")
    st.markdown(
        "- [Pinto Protocol](https://pinto.money)\n"
        "- [Pinto Docs](https://docs.pinto.money)\n"
        "- [Pinto Github](https://github.com/pinto-org/protocol)\n"
        "- [Pinto Discord](https://pinto.money/discord)"
    )


main()
