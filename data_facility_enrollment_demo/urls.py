from django.contrib import admin
from django.urls import include, path
from data_facility_enrollment_demo import views

urlpatterns = [
    path("", views.index, name="index"),
    path("onboarding/", views.onboarding, name="onboarding"),
    path(
        "create_guest_collection/",
        views.guest_collection,
        name="create-guest-collection",
    ),
    path("thanks/", views.onboarding_complete, name="onboarding-complete"),
    path("admin/", admin.site.urls),
    path("", include("globus_portal_framework.urls")),
    path("", include("social_django.urls", namespace="social")),
]
