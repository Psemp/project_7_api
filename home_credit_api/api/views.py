from django.http import JsonResponse
from rest_framework.decorators import api_view

from api.models import Estimator
from api.scripts.predict_functions import predict_id, load_dataset


@api_view(["GET"])
def predict_view(request):
    client_id = int(request.GET.get("client_id"))
    model_id = request.GET.get("model_id")

    if not client_id or not model_id:
        return JsonResponse({"error": "client_id and model_id are required query parameters"}, status=400)

    try:
        estimator = Estimator.objects.get(identifier=model_id)
    except Estimator.DoesNotExist:
        return JsonResponse({"error": f"No estimator found for model id {model_id}"}, status=404)

    try:
        classifier = estimator.get_classifier()
    except Exception as e:
        return JsonResponse({"error": f"Failed to load model for model {model_id}: {e}"}, status=500)

    shap_values = estimator.get_shap_values()

    dataframe = load_dataset(dataset_path="data/df_predict.pkl")

    dataframe = dataframe.loc[:, ~dataframe.columns.duplicated()].copy()

    if client_id not in dataframe["SK_ID_CURR"].values:
        return JsonResponse({"error": f"{client_id} not in dataset"}, status=404)

    try:
        credit_score, adjusted_shap_vals = predict_id(
            classifier=classifier,
            sk_id=client_id,
            clf_shap=shap_values,
            dataset=dataframe,
        )
    except Exception as e:
        return JsonResponse({"error": f"Failed to predict score for client {client_id}: {e}"}, status=500)

    response = {
        "credit_score": credit_score,
        "shap_values": adjusted_shap_vals.tolist(),
        "shap_columns": shap_values.feature_names
    }

    return JsonResponse(response, status=200)


@api_view(["GET"])
def id_list(request):

    dataframe = load_dataset(dataset_path="data/df_predict.pkl")

    dataframe = dataframe.loc[:, ~dataframe.columns.duplicated()].copy()

    try:
        ids = dataframe["SK_ID_CURR"].values.tolist()
    except Exception as e:
        return JsonResponse({"error": f"Failed to load client list | {e}"}, status=500)

    response = {
        "ids": ids,
    }

    return JsonResponse(response, status=200)
