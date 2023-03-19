import os
import json

from django.core.management.base import BaseCommand
from django.core.files import File
from api.models import Estimator


class Command(BaseCommand):
    help = "Load an estimator model from a directory and save it to the database"

    def add_arguments(self, parser):
        parser.add_argument("model_dir", type=str, help="The directory where the model files are stored")
        parser.add_argument("model_name", type=str, help="The name of the model")

    def handle(self, *args, **options):
        model_dir = options["model_dir"]
        model_name = options["model_name"]

        # Create file paths based on the directory and file names
        classifier_path = os.path.join(model_dir, "classifier.pkl")
        shap_values_path = os.path.join(model_dir, "shap_values.pkl")
        columns_path = os.path.join(model_dir, "columns_name.json")
        metrics_path = os.path.join(model_dir, "metrics.json")

        # Create Django File objects from the files
        classifier_file = File(open(classifier_path, "rb"))
        shap_values_file = File(open(shap_values_path, "rb"))
        columns_file = File(open(columns_path, "r"))
        metrics_file = File(open(metrics_path, "r"))

        # Preprocess the columns_train and metrics fields
        columns_train = json.loads(columns_file.read().replace("\n", "").replace(" ", ""))
        metrics = json.loads(metrics_file.read().replace("\n", "").replace(" ", ""))

        # Create an instance of the Estimator model
        estimator = Estimator(
            name=model_name,
            classifier=classifier_file,
            shap_values=shap_values_file,
            columns_train=columns_train,
            metrics=metrics,
        )

        estimator.save()

        self.stdout.write(self.style.SUCCESS(f"""
        Successfully loaded {model_name} from {model_dir} and saved it to the database."""))
