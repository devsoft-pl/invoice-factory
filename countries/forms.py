from django import forms
from django.utils.translation import gettext as _

from countries.models import Country


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
        land = Country.objects.filter(country=country, user=self.user)

        if land.exists():
            raise forms.ValidationError(_("Country already exists"))

        return country
