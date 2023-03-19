import streamlit as st
import requests
import os
import urllib

from dotenv import load_dotenv
from matplotlib import pyplot as plt
from matplotlib import colors as mcolors

from streamlit_scripts.queries import get_table_objects
from streamlit_scripts.shap_utils import create_shap_frame, create_waterfall_plot

load_dotenv()
plt.style.use('Solarize_Light2')

try:
    server_host = os.environ["SERVER_HOST"]
    server_port = os.environ["SERVER_PORT"]
except KeyError:
    server_host = "localhost"
    server_port = "8000"

api_url = f"http://{server_host}:{server_port}"


def overview():
    st.title("Dashboard overview")

    # Display basic info about models, metrics, and scores
    overview_text = """
    ## About the Dashboard
    &emsp;This dashboard provides machine learning models for assessing client risk.
    The models are designed to be transparent and explainable, with a focus on interpretability.
    The app takes a client ID as input and returns a risk score indicating the likelihood of risk.
    The score is based on a set of models trained on historical data and can be used to inform decisions
    such as whether to approve or deny a loan.

    ## Key Features

    - **Transparent and explainable:** For each prediction, the app provides a detailed explanation of how\
the model arrived at its decision, including the specific features of the data that contributed to the prediction.
    - **Interpretable:** The models are designed\
to be easily interpretable, with clear explanations for each prediction.
    - **User-friendly interface:** The app is designed to provide a clear, accessible interface\
for assessing client risk and making informed decisions based on machine learning models.

    ## TL;DR
    &emsp;Overall, this dashboard provides a powerful tool for assessing client risk, with a focus on transparency and
    interpretability. With clear explanations for each prediction and an easy-to-use interface,
    Although, it is important to keep in mind that the models provide suggestions,
    the aim is to provide the tools to make in informed choice, not make the choice itself.
    """

    st.markdown(overview_text)


def model_overview():

    st.title("Model Overview")

    model_dict = get_models()

    # Allow user to select which model to use
    model_options = model_dict.keys()
    selected_model_name = st.selectbox("Select a model", model_options)
    selected_model = None
    for estimator in model_options:
        if estimator == selected_model_name:
            selected_model = estimator
            break

    # Display model stats, metrics, parameters, and SHAP plot

    run_metrics = model_dict[selected_model][0]

    # Metrics in HTMLish table
    st.write("Selected model metrics:")
    metrics_table = "<table><tr><th>Metric</th><th>Value</th></tr>"
    for metric_name, metric_value in run_metrics.items():
        metrics_table += f"<tr><td>{metric_name}</td><td>{metric_value}</td></tr>"
    metrics_table += "</table>"
    st.write(metrics_table, unsafe_allow_html=True)

    st.write("\n")
    st.write("\n")

    # path to plots
    auc_conf_plot_path = model_dict[selected_model][1]
    shap_plot_path = model_dict[selected_model][2]

    # hide with expander
    with st.expander("Feature importance Summary"):
        st.image(shap_plot_path, use_column_width=True)
    with st.expander("AUC / Confusion Matrix"):
        st.image(auc_conf_plot_path, use_column_width=True)


def prediction(models: list):
    st.title("Prediction")

    model_dict = get_models()

    # Allow user to select which model to use
    model_options = model_dict.keys()
    selected_model_name = st.selectbox("Select a model (default = xGboost)", model_options, index=0)
    selected_model = None
    for model in model_options:
        if model == selected_model_name:
            selected_model = model
            break

    ###
    # Gets all the ids for autocompletion but autcomplete excepects a string not a list
    # request_list = get_client_list()
    # if request_list["response_code"] == 200:
    #     client_list = request_list["id_list"]
    # else:
    #     client_list = None

    client_id = st.text_input("Enter client ID", "", autocomplete=None)

    selected_model_id = model_dict[selected_model][3]

    if st.button("Predict"):

        params = {"client_id": client_id, "model_id": selected_model_id}
        response_dict = api_call(params=params)

        if response_dict["response_code"] == 200:
            client_score = response_dict["credit_score"]
            local_shap_values = response_dict["shap_values"]
            shap_columns = response_dict["shap_columns"]

            df_shap = create_shap_frame(shap_values=local_shap_values, feature_names=shap_columns)

            waterfall = create_waterfall_plot(df_shap=df_shap, base_value=client_score)

            score_color = get_gradient(client_score)

            html_code = f"""
            <div style="width: 25%; margin: auto;">
                <div style="background-color: {score_color}; border-radius: 2rem; padding: .2rem;">
                    <p style="font-size: 1.9rem; text-align: center; color: black;">Score: {client_score}/100</p>
                </div>
            </div>
            """

            st.markdown(html_code, unsafe_allow_html=True)

            st.write("\n")

            with st.expander("Feature explanation chart"):
                st.pyplot(fig=waterfall)
        elif response_dict["response_code"] != 200:
            st.error(f"Error : {response_dict['response_code']} - {response_dict['verbose_error']}")


def api_call(params: dict):
    api_endpoint = "/api/predict/?"
    request_url = f"{api_url}{api_endpoint}{urllib.parse.urlencode(params)}"
    headers = {}
    response = requests.get(request_url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        credit_score = data["credit_score"]
        shap_values = data["shap_values"]
        shap_columns = data["shap_columns"]

        request_response_dict = {
            "response_code": response.status_code,
            "credit_score": credit_score,
            "shap_values": shap_values,
            "shap_columns": shap_columns
            }

        return request_response_dict

    else:
        response_code = response.status_code
        verbose_error = response.json()["error"]

        request_response_dict = {
            "response_code": response_code,
            "verbose_error": verbose_error,
            }

        return request_response_dict


def make_prediction(model, client_id):

    url = f"{api_url}/{client_id}/{model}"
    response = requests.get(url)

    # Display results in Streamlit app
    if response.status_code == 200:
        data = response.json()
        score = data.get("score")
        shap_plot = data.get("shap_plot")
        model_summary = data.get("model_summary")

        st.write(f"Score for client {client_id} using model {model}: {score}")
        st.write(shap_plot)
        st.write(model_summary)
    else:
        st.write("Error: Unable to retrieve prediction results")


def get_models():
    results = get_table_objects(table="api_estimator")
    models = {}
    for result in results:
        # model name = metrics, auc_conf_image, shap_plot, identifier
        model_name = result[0]
        metrics = result[1]
        auc_conf_image_path = os.path.abspath(result[2])
        shap_plot_path = os.path.abspath(result[3])
        identifier = result[4]
        models[model_name] = (metrics, auc_conf_image_path, shap_plot_path, identifier)

    return models


def get_gradient(score: int) -> str:
    """
    Uses the matplotlib colormap "autumn" to get a color in range score

    Args :
    - score : integer score of the client

    Returns
    - hex_color : the color in hexadecimal for html/css
    """

    # Using autumn
    # ref here : https://matplotlib.org/stable/gallery/color/colormap_reference.html
    cmap = plt.get_cmap("autumn")

    # Placing the value on the colormap
    color = cmap(score / 100)

    hex_color = mcolors.to_hex(color)

    return hex_color


def get_client_list():
    api_endpoint = "/api/get_ids/"
    request_url = f"{api_url}{api_endpoint}"
    headers = {}
    response = requests.get(request_url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        id_list = data["ids"]

        request_response_dict = {
            "response_code": response.status_code,
            "id_list": id_list
            }

        return request_response_dict

    else:
        response_code = response.status_code
        verbose_error = response.json()["error"]

        request_response_dict = {
            "response_code": response_code,
            "verbose_error": verbose_error,
            }

        return request_response_dict
