import pickle

from django.db import models


class Estimator(models.Model):
    identifier = models.AutoField(primary_key=True, auto_created=True)
    name = models.CharField(max_length=255, blank=False)
    classifier = models.FileField(upload_to="classifiers/", blank=True)
    shap_values = models.FileField(upload_to="shap_values/", blank=True)
    columns_train = models.JSONField()
    metrics = models.JSONField()
    auc_conf_image = models.ImageField(upload_to="plots/", blank=True)
    summary_image = models.ImageField(upload_to="plots/", blank=True)

    def get_classifier(self):
        if not self.classifier:
            raise ValueError("Classifier not uploaded, please use the admin interface to do so")
        else:
            try:
                with self.classifier.open(mode="rb") as f:
                    classifier_bytes = f.read()
                    classifier = pickle.loads(classifier_bytes)
                    return classifier
            except Exception as e:
                raise ValueError(f"Error loading classifier: {e}")

    def get_shap_values(self):
        if self.shap_values is None:
            raise ValueError("SHAP values not uploaded, please use the admin interface to do so")
        else:
            with self.shap_values.open(mode="rb") as f:
                shap_values = pickle.load(f)
            return shap_values

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name
