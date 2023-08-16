from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings

from data_facility_enrollment_demo.arc_api import ARCClient

from data_facility_enrollment_demo.gcs import (
    lookup_guest_collections,
    create_acl,
    verify_valid_guest_collection,
)
from data_facility_enrollment_demo.search import create_search_record
from data_facility_enrollment_demo.forms import OnboardingForm


def index(request):
    return render(request, "index.html", {})


@login_required
def onboarding(request):
    arc_client = ARCClient(request.user)
    arc = {
        "projects": arc_client.get_projects(),
        "storage": arc_client.get_storage(),
    }
    context = {"arc": arc, "guest_collections": lookup_guest_collections(request.user)}

    if request.method == "POST":
        form = OnboardingForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["guest_collection"] == "create_new":
                return redirect("create-guest-collection")
            elif verify_valid_guest_collection(request.user, form.cleaned_data["guest_collection"], settings.GUEST_COLLECTION_REQUIRED_GROUP):
                return redirect("onboarding-complete")
            else:
                context["errors"] = "Guest collection is invalid!"
    else:
        form = OnboardingForm()
    context["form"] = form
    return render(request, "onboarding.html", context)


@login_required
def create_guest_collection(request):
    context = {
        "mapped_collections": settings.AVAILABLE_MAPPED_COLLECTIONS,
    }
    if request.method == "POST":
        form = OnboardingForm(request.POST)
        if form.is_valid():
            # create_search_record(project_id, collection_id, request.user)
            # create_acl(request.user)
            return redirect("onboarding-complete")
    else:
        form = OnboardingForm()
    return render(request, "create-guest-collection.html", context)


@login_required
def onboarding_complete(request):
    context = {}
    return render(request, "onboarding-complete.html", context)
