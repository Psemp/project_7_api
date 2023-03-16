import os
import mlflow

from django.core.management.base import BaseCommand, CommandError
from api.models import Estimator


class Command(BaseCommand):
    help = """
    Register a new ML model in the database, arm yourself with a notepad
    Args :
    - model_name : the model name, on mlflow
    - run_id : the mlflow run id (on the UI)
    - model_type : the type of the model (xgboost, catboost) at the moment

    """

    def add_arguments(self, parser):
        parser.add_argument("model_name", type=str, help="Name of the model")
        parser.add_argument("run_id", type=str, help="MLflow run ID for the model")
        parser.add_argument("model_type", type=str, choices=["xgboost", "catboost"], help="Type of the model")

    def handle(self, *args, **options):
        model_name = options["model_name"]
        run_id = options["run_id"]
        model_type = options["model_type"]

        try:
            mlflow_client = mlflow.tracking.MlflowClient()
            mlflow_client.get_run(run_id)
        except Exception:
            raise CommandError(f"Could not find run with ID {run_id}")

        if Estimator.objects.filter(mlflow_run_id=options["run_id"]).exists():
            self.stdout.write(self.style.WARNING("Model already registered with this run id. Skipping."))
            return

        if model_type == "xgboost":
            model_path = os.path.join(f"runs:/{run_id}/xGboost-model")
        elif model_type == "catboost":
            model_path = os.path.join(f"runs:/{run_id}/catboost-model")
        else:
            raise CommandError("Invalid model type")

        estimator = Estimator(
            estimator_name=model_name,
            mlflow_run_id=run_id,
            model_path=model_path,
            estimator_type=model_type,
        )
        estimator.save()

        self.stdout.write(self.style.SUCCESS(f"Successfully registered {model_name} as a {model_type} model"))
