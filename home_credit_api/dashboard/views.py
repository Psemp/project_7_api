from django.shortcuts import render


def dashboard(request):
    context = {"is_dashboard": True}

    return render(request, "dashboard/dashboard.html", context)
