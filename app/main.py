import streamlit as st
from data import gather_data
from st_copy_to_clipboard import st_copy_to_clipboard


def custom_css():
    st.html("""
        <style>
            footer {visibility: hidden;}
            MainMenu {visibility: hidden;}
            /*
            @font-face {
                font-family: Pinto;
                font-weight: 500;
                font-display: swap;
                src: url(https://pinto.money/assets/Pinto-Regular-fAgL6fz7.woff2) format("woff2")
            }

            @font-face {
                font-family: Pinto;
                font-weight: 400;
                font-display: swap;
                src: url(https://pinto.money/assets/Pinto-Book-qJmluawK.woff2) format("woff2")
            }

            @font-face {
                font-family: Pinto;
                font-weight: 340;
                font-display: swap;
                src: url(https://pinto.money/assets/Pinto-Book-qJmluawK.woff2) format("woff2")
            }

            @font-face {
                font-family: Pinto;
                font-weight: 300;
                font-display: swap;
                src: url(https://pinto.money/assets/Pinto-Light-B9ltJaNi.woff2) format("woff2")
            }

            @font-face {
                font-family: Pinto;
                font-weight: 600;
                font-display: swap;
                src: url(https://pinto.money/assets/Pinto-Medium-SzILf3-D.woff2) format("woff2")
            }

            @font-face {
                font-family: Roboto;
                font-weight: 300;
                font-display: swap;
                src: url(https://pinto.money/assets/Roboto-Light-BW8nAIZg.ttf) format("truetype")
            }

            html, body, p, [class*="css"]  {
                font-family: "Pinto", "Source Sans Pro", sans-serif;
                font-weight: 340;
                color: rgb(169, 162, 151);
            }

            h1, h2, h3 {
                font-family: "Pinto", "Source Sans Pro", sans-serif;
                font-weight: 300;
            }
            */
        </style>
    """)


def disclaimers():
    with st.popover("Disclaimers", use_container_width=True):
        st.warning(
            "This application is for informational purposes only and is not "
            "representative of financial advice. Please do your own research."
        )
        st.warning(
            "This application is in active development and the data may be inaccurate."
        )


def main():
    """This drives the entire streamlit application"""

    st.set_page_config(
        page_title="Pinto Analytics",
        page_icon="https://pinto.money/assets/PINTO-Dzfg2sTm.png",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            "Get Help": "https://pinto.money/discord",
            "Report a bug": "https://github.com/0xMochan/pinto-analysis/issues",
            "About": "This app showcases some data analysis on the Pinto Protocol",
        },
    )

    custom_css()

    data = gather_data()

    with st.expander("Data Debug"):
        st.write(data.latest_season)

    with st.sidebar:
        left, right = st.columns(2, vertical_alignment="center")
        with left:
            disclaimers()
        right.button(
            "Refresh Data", on_click=st.cache_data.clear, use_container_width=True
        )
        st.divider()
        st.markdown(
            "🌱 **Current Season** ・ {}".format(int(data.latest_season["season"]))
        )
        price = float(data.latest_season["price"])
        color = "#72be95" if price > 1 else "#e57373"
        st.markdown(
            "<p>🏷️ <strong>Seasonal Price</strong> ・ "
            f'<span style="color:{color}">$ {price:.6f}</span></p>',
            unsafe_allow_html=True,
        )
        st.divider()
        st.markdown("*By [0xMochan](https://twitter.com/0xMochan)*")
        st.markdown("Shoot me some Pinto if you liked this app!")
        st.markdown("`0xe23cE0f5dC9D3DA1FD69d3A169F5596F5A5669AA`")
        st_copy_to_clipboard(
            "0xe23cE0f5dC9D3DA1FD69d3A169F5596F5A5669AA",
            before_copy_label="📋 Click to copy!",
            after_copy_label="✅ Copied!",
        )

    st.navigation(
        {
            "Home": [
                st.Page("main.py", title="🏡 Homepage"),
                st.Page("about.py", title="📚 About"),
            ],
            "Data Apps": [
                st.Page("protocol.py", title="🏗️ Protocol Overview"),
                st.Page("flood.py", title="🌊 Flood Inspector"),
                st.Page("field.py", title="🌾 Field Analytics"),
                # st.Page("portfolio.py", title="📊 Portfolio Viewer"),
            ],
        }
    ).run()


if __name__ == "__main__":
    main()
