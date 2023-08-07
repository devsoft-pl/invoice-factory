from django import forms

from countries.models import Country
from django.utils.translation import gettext as _


class CountryForm(forms.ModelForm):
    next = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    class Meta:
        model = Country
        fields = ["next", "country"]

    def clean_country(self):
        country = self.cleaned_data.get("country")
        country = Country.objects.filter(country=country, user=self.user)

        if country.exists():
            raise forms.ValidationError(_("Country already exists"))

