from django.shortcuts import render, redirect
from data_facility_enrollment_demo.arc_api import ARCClient


def onboarding(request):
    arc_client = ARCClient(request.user)
    arc = {
        "projects": arc_client.get_projects(),
        "storage": arc_client.get_storage(),
    }
    context = {"arc": arc}

    if request.method == "POST":
        return redirect("onboarding-complete")

    return render(request, "onboarding.html", context)


def onboarding_complete(request):
    context = {}
    return render(request, "onboarding-complete.html", context)
