from django import forms
from django.utils.translation import gettext_lazy as _

from countries.models import Country


class CountryForm(forms.ModelForm):
    def __init__(self, current_user, *args, **kwargs):
        self.current_user = current_user
        super().__init__(*args, **kwargs)

        country_field: forms.CharField = self.fields["country"]
        country_field.widget.attrs["class"] = "form-control"

    class Meta:
        model = Country
        fields = ["country"]

    def clean_country(self):
        country = self.cleaned_data.get("country")
        land = Country.objects.filter(country=country, user=self.current_user)

        if land.exists():
            raise forms.ValidationError(_("Country already exists"))

        return country
