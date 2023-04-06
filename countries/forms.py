from django import forms

from countries.models import Country


class CountryForm(forms.ModelForm):
    class Meta:
        model = Country
        fields = ["country"]
