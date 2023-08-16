from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from data_facility_enrollment_demo.arc_api import ARCClient

from data_facility_enrollment_demo.gcs import lookup_gcs_stuff, create_acl
from data_facility_enrollment_demo.search import create_search_record


def index(request):

    return render(request, "index.html", {})


@login_required
def onboarding(request):
    arc_client = ARCClient(request.user)
    arc = {
        "projects": arc_client.get_projects(),
        "storage": arc_client.get_storage(),
    }
    context = {"arc": arc}

    lookup_gcs_stuff(request.user)

    if request.method == "POST":
        create_search_record(request.user)
        create_acl(request.user)
        return redirect("onboarding-complete")

    return render(request, "onboarding.html", context)


@login_required
def onboarding_complete(request):
    context = {}
    return render(request, "onboarding-complete.html", context)
