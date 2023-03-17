import os
import pickle

import numpy as np
import pandas as pd


def load_dataset(dataset_path):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_path = os.path.join(base_dir, dataset_path)
    with open(dataset_path, "rb") as f:
        dataset = pickle.load(f)
    return dataset


def predict_id(classifier, sk_id, clf_shap, dataset: pd.DataFrame):
    """
    Uses the classifier passed in argument to predict result of a single row
    defined by sk_id. Computes the local shap values

    Args :
    - classifier : the estimator used to predict_proba
    - sk_id : the client identifier used to base the prediction
    - clf_shap : the global shap values of the classifier, precomputed to save time
    - dataset : the pandas dataframe with the row of the client inside

    Returns :
    - credit_score : modified score via adapt_score_shap()
    - adjusted_shap_vals: modified shap values via adapt_score_shap()
    """

    try:
        client_row = dataset.loc[dataset["SK_ID_CURR"] == int(sk_id)]
        client_row = client_row.drop(columns=["SK_ID_CURR"])
    except KeyError:
        raise ValueError(f"SK_ID_CURR {sk_id} not found in dataset")

    inital_score = classifier.predict_proba(client_row)

    initial_shap_values = clf_shap.values[client_row.index[0]]

    credit_score, adjusted_shap_vals = adapt_score_shap(
        initial_score=inital_score,
        initial_shap_values=initial_shap_values
    )

    return credit_score, adjusted_shap_vals


def adapt_score_shap(initial_score, initial_shap_values):
    """
    Adapting the proba of the prediction (0 > 1, good > bad)
    to base 100 and reversing it (0 bad > 100 good)
    Doing the same for the SHAP values for interpretability.

    Args:
    - initial_score : the initial score from the classifier (range 0, 1)
    - initial_shap_values : local shap values calculated from the instance

    Returns:
    - score : the base 100 score
    - normalized_shap_values : inverted and scaled 100 fold shap values
    """
    # Adjusting score (0 = bad , 100 good)
    score = (1 - initial_score[:, 1]) * 100  # converting proba to base 100
    score = int(score)  # rounding and converting to int

    normalized_shap_values = np.negative(initial_shap_values) * 100

    return score, normalized_shap_values
