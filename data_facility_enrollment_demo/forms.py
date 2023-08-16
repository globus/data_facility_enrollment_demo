from django import forms


class OnboardingForm(forms.Form):
    source_col = forms.CharField(label="Source Collection", max_length=128)
    source_path = forms.CharField(label="Source Path", max_length=256)
