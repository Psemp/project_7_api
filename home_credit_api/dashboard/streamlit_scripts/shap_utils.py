import numpy as np
import pandas as pd

from matplotlib import pyplot as plt


def create_shap_frame(shap_values: list, feature_names: list) -> pd.DataFrame:
    """
    Takes the returns from the API : the shap_values and associated feature names
    Creates a DataFrame from the values and sort it by abs(shap_value) in descending order

    Args:
    - shap_values : list of the shap values (API return a list of list, hence the flatten)
    - feature_namess : list of the feature names

    Returns :
    - df_shap : dataframe ordered by descending absolute shap value
    """

    data_shap = {"shap_values": np.array(shap_values).flatten(), "feature_names": feature_names}
    df_shap = pd.DataFrame(data=data_shap)

    df_shap = df_shap.reindex(df_shap["shap_values"].abs().sort_values(ascending=False).index)
    df_shap.reset_index(inplace=True, drop=True)

    return df_shap


def create_waterfall_plot(df_shap: pd.DataFrame, base_value: int, limit: int = 20):
    """
    Uses the dataframe containing shap values to recreate waterfall plot explainer.

    Args :
    - df_shap : dataframe containing shap_values, shap_columns
    - base_value : integer, the score of the local instance
    - limit : int, how many features to display, default 20, can be adjusted
    """

    plt.ioff()

    df_shap = df_shap.head(limit).copy()
    df_shap["shap_values"] = df_shap["shap_values"].apply(lambda x: round(x, ndigits=2))

    df_shap["cum_shap_values"] = df_shap["shap_values"].cumsum()
    df_shap["cum_shap_values"] = df_shap["cum_shap_values"].apply(lambda x: round(x, ndigits=2))

    df_plot = df_shap.head(n=limit)

    fig, (ax1) = plt.subplots(
        ncols=1,
        nrows=1,
        figsize=(8, 12),
        dpi=155,
    )
    ax1.barh(
        df_plot.index,
        df_plot["shap_values"],
        align="center",
        color=df_plot["shap_values"].apply(lambda x: "#AB2328" if x < 0 else "#000331"))

    bbox_values = {
        "facecolor": "black",
        "edgecolor": "none",
        "boxstyle": "round"
        }

    for index, row in df_plot.iterrows():
        shap_val = row["shap_values"]
        ax1.text(
            shap_val,
            index,
            f"{shap_val}", ha="left" if shap_val < 0 else "right",
            va="center",
            bbox=bbox_values,
            color="w"
            )

    final_val = df_shap["cum_shap_values"].iloc[-1]
    fig.suptitle(f"Model output value (adjusted by SHAP) = {round(final_val, 4)})")

    ax1.set_yticks(df_plot.index)
    ax1.set_yticklabels(df_plot["feature_names"], fontsize=8)
    ax1.tick_params(axis="y", labelsize=8)
    ax1.invert_yaxis()

    fig.tight_layout()
    return plt.gcf()
