import streamlit as st

from matplotlib import pyplot as plt

from streamlit_scripts.streamlit_pages import overview, model_overview, prediction, get_models


plt.style.use('Solarize_Light2')


def dashboard():
    st.set_page_config(
        page_title="Dashboard",
        page_icon=":guardsman:",
        layout="wide",
        )

    pages = ["Overview", "Model overview", "Predict Home Credit Score"]
    pages = {
        "Overview": overview,
        "Model overview": model_overview,
        "Predict Home Credit Score": prediction,
    }

    models = get_models().keys()
    page = st.sidebar.selectbox("Select a page", list(pages.keys()))

    if page == "Overview":
        overview()

    elif page == "Model overview":
        model_overview()

    elif page == "Predict Home Credit Score":
        prediction(models=models)


if __name__ == '__main__':
    dashboard()
