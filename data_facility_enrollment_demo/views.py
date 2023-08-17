import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings

from data_facility_enrollment_demo.arc_api import ARCClient

from data_facility_enrollment_demo.gcs import (
    create_guest_collection,
    lookup_guest_collections,
    create_acl,
    verify_guest_collection_permissions,
    verify_guest_collection_keywords,
)
from data_facility_enrollment_demo.search import create_search_record

from data_facility_enrollment_demo.forms import OnboardingForm
from data_facility_enrollment_demo.forms import CreateGuestCollectionForm
from data_facility_enrollment_demo.exc import MissingKeyword

log = logging.getLogger(__name__)


def index(request):
    return render(request, "index.html", {})


@login_required
def onboarding(request):
    arc_client = ARCClient(request.user)
    arc = {
        "projects": arc_client.get_projects(),
        "storage": arc_client.get_storage(),
    }

    context = {"arc": arc, "projects": arc["projects"], "guest_collections": lookup_guest_collections(
        request.user, settings.GUEST_COLLECTION_REQUIRED_KEYWORD)}

    if request.method == "POST":
        form = OnboardingForm(request.POST)
        if form.is_valid():
            request.session['project_id'] = form.cleaned_data["project"]
            if form.cleaned_data["guest_collection"] == "create_new":
                return redirect("create-guest-collection")
            try:
                verify_guest_collection_permissions(
                    request.user, form.cleaned_data["guest_collection"], settings.GUEST_COLLECTION_REQUIRED_GROUP)
                verify_guest_collection_keywords(
                    request.user,  form.cleaned_data["guest_collection"], settings.GUEST_COLLECTION_REQUIRED_KEYWORD)
                return redirect("onboarding-complete")
            except MissingKeyword as mk:
                log.error(mk)
                context['errors'] = mk
                context['error_link'] = f'https://app.globus.org/file-manager/collections/{form.cleaned_data["guest_collection"]}/overview'
    else:
        form = OnboardingForm()
    context["form"] = form
    return render(request, "onboarding.html", context)


@login_required
def guest_collection(request):
    context = {
        "mapped_collections": settings.AVAILABLE_MAPPED_COLLECTIONS,
    }
    if request.method == "POST":
        form = CreateGuestCollectionForm(request.POST)
        log.info(f" is form valid ?{form.is_valid()}")
        if form.is_valid():
            create_search_record(
                request.session['project_id'], "collectionuuid", request.user)
            # create_acl(request.user)
            create_guest_collection(
                "Guest Collection",
                form.cleaned_data["endpoint_hostname"],
                form.cleaned_data["endpoint_id"],
                form.cleaned_data["mapped_collection_id"],
                form.cleaned_data["storage_gateway_id"],
                request.user)
            return redirect("onboarding-complete")
        else:
            log.error(form)
    else:
        form = CreateGuestCollectionForm()
    return render(request, "create-guest-collection.html", context)


@login_required
def onboarding_complete(request):
    context = {}
    return render(request, "onboarding-complete.html", context)
