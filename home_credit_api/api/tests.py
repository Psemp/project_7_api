from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Estimator


class EstimatorTest(TestCase):

    def setUp(self) -> None:
        dummy_metrics = {
            "auc": 0.5,
            "f1": 0.55,
            "recall": 0.6,
            "accuracy": 0.65,
            }

        self.info = {
            "identifier": 10,
            "name": "test model",
            "columns_train": {"columns": ["col1", "col2", "col3"]},
            "metrics": dummy_metrics,
        }

        Estimator.objects.create(**self.info)

        def test_estimator_test(self):
            test_est = Estimator.objects.get(name="test model")
            self.assertequal(test_est.name, "test model")
            self.assertequal(test_est.identifier, 10)
            self.assertin(test_est.columns_train["columns"], ["col1", "col2", "col3"])
            self.assertin(test_est.metrics.keys(), ["auc", "f1", "recall", "accuracy"])


class PredictViewTestCase(APITestCase):
    def test_predict_view_with_invalid_parameters(self):
        url = reverse("predict")
        data = {"client_id": 10, "model_id": 999}
        response = self.client.get(url, data)

        # Model not found, client not found --> 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_predict_view_with_invalid_estimator(self):
        client_id = 123456
        model_id = 123

        url = reverse("predict")
        data = {"client_id": client_id, "model_id": model_id}
        response = self.client.get(url, data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
