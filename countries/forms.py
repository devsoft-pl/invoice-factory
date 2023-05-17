from django import forms

from countries.models import Country


class CountryForm(forms.ModelForm):
    next = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Country
        fields = ["next", "country"]

