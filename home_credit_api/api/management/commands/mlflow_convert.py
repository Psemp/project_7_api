import os
import mlflow
import urllib
import pickle

from django.core.management.base import BaseCommand

from api.models import Estimator


class Command(BaseCommand):
    help = "Loads an MLFlow model run into a Django model"

    def add_arguments(self, parser):
        parser.add_argument("mlflow_model_name", type=str, help="Name of the MLFlow model")
        parser.add_argument("mlflow_run_id", type=str, help="ID of the MLFlow run")
        parser.add_argument("verbose_name", type=str, help="Display name for the Django model")
        parser.add_argument("model_type", type=str, help="Type of the ML model (xgboost or catboost)")

    def handle(self, *args, **options):
        mlflow_model_name = options["mlflow_model_name"]
        mlflow_run_id = options["mlflow_run_id"]
        verbose_name = options["verbose_name"]
        model_type = options["model_type"]

        model_dict = glabber(mlflow_model_name, mlflow_run_id, verbose_name, model_type)

        classifier = model_dict["estimator"]
        shap_values = model_dict["shap_global_values"]

        with open("classifier.pkl", "wb") as f:
            pickle.dump(classifier, f)

        # save shap_values as pickle
        with open("shap_values.pkl", "wb") as f:
            pickle.dump(shap_values, f)

        # create estimator object
        estimator = Estimator(
            name=verbose_name,
            metrics=model_dict["metrics"],
            columns_train=model_dict["train_columns"],
        )
        estimator.save()


def glabber(mlflow_model_name: str, mlflow_run_id: str, verbose_name: str, model_type: str) -> dict:
    """
    Uses an MLFlow run to recover the model and all relevant informations for django storage

    Args :
    - mlflow_model_name : the name of the model as logged on mlflow
    - mlflow_run_id : the id of the mlflow run of the model
    - verbose_name : the display name of the model, for readable interface
    - model_type : xgboost or catboost, to define what mlflow function is needed to load the model

    Returns :
    """

    if str.lower(model_type) == "xgboost":
        model_path = os.path.join("runs:/", mlflow_run_id, "xGboost-model")
        estimator = mlflow.xgboost.load_model(model_uri=model_path)
    elif str.lower(model_type) == "catboost":
        model_path = os.path.join("runs:/", mlflow_run_id, "catboost-model")
        estimator = mlflow.catboost.load_model(model_uri=model_path)

    run = mlflow.get_run(run_id=mlflow_run_id)

    artifact_uri = run.info.artifact_uri

    shap_file = "shap_values/shap_values.pkl"
    columns_file = "columns_train/columns_train.pkl"
    auc_curve_file = "AUROC_Conf_matrix.png"
    shap_plot_file = "summary_shap.png"

    metrics = run.data.metrics
    model_name = verbose_name

    shap_path = os.path.join(artifact_uri, shap_file)
    shap_path = urllib.parse.urlparse(shap_path).path

    columns_path = os.path.join(artifact_uri, columns_file)
    columns_path = urllib.parse.urlparse(columns_path).path

    auc_plot_path = os.path.join(artifact_uri, auc_curve_file)
    auc_plot_path = urllib.parse.urlparse(auc_plot_path).path

    shap_summary_path = os.path.join(artifact_uri, shap_plot_file)
    shap_summary_path = urllib.parse.urlparse(shap_summary_path).path

    with open(shap_path, "rb") as shap_pkl:
        shap_values = pickle.load(shap_pkl)

    with open(columns_path, "rb") as col_pkl:
        model_columns = pickle.load(col_pkl)

    model_dict = {
        "estimator": estimator,
        "model_name": model_name,
        "metrics": metrics,
        "shap_global_values": shap_values,
        "train_columns": model_columns,
        "auc_conf_image": auc_plot_path,
        "summary_image": shap_summary_path,
    }

    return model_dict
