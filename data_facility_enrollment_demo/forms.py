from django import forms


class OnboardingForm(forms.Form):
    project = forms.CharField(label="Project", max_length=256)
    guest_collection = forms.CharField(
        label="Guest Collection", max_length=256)


class CreateGuestCollectionForm(forms.Form):
    mapped_collection_id = forms.CharField(label="Collection", max_length=256)
    endpoint_hostname = forms.CharField(
        label="Collection URL", max_length=256)
    endpoint_id = forms.CharField(
        label="Endpoint ID", max_length=256
    )
    storage_gateway_id = forms.CharField(
        label="Storage Gateway ID", max_length=256)
    base_path = forms.CharField(
        label="Base Path", max_length=256, required=False)
