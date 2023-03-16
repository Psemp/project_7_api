import pandas as pd
import mlflow
import shap

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = ""

    def add_arguments(self, parser):
        parser.add_argument("model_id", nargs='+', type=int)


def get_local_feature_importance():
    ...


def modify_score_proba(score, shap_values):
    """
    Estimators have been trained to detect 1 as possible payment difficulties, 0 as unlikely.
    Changing it to a base 100 score with 100: high confidence. Same for local shap values.

    Args :
    - score : the score of the client predicted with estimator.predict_proba
    - the local shap_value

    Returns :
    - adjusted_credit_score : the score adjusted on base 100 and reversed
    - ajusted_shap_values : the shap values adjusted in the same way
    """

    adjusted_credit_score = (1 - score) * 100
    ajusted_shap_values = (1 - shap_values) * 100

    return adjusted_credit_score, ajusted_shap_values


def predict_id(model_name: str, file_path: str, model_type: str, sk_id: int):

    model_name = "my_model_name"
    model_uri = f"models:/{model_name}"
    columns_train = ""
    model_shap_values = ""

    match model_type:
        case "sklearn":
            model = mlflow.sklearn.load_model(model_uri)
        case "xgboost":
            model = mlflow.xgboost.load_model(model_uri)
        case "tensorflow":
            model = mlflow.tensorflow.load_model(model_uri)

    dataframe_predict = pd.read_pickle(filepath_or_buffer=file_path)

    label = model.predict_proba(dataframe_predict[dataframe_predict["SK_ID_CURR"] == sk_id][columns_train])
