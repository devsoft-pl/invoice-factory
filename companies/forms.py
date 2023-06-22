from django import forms
from django.utils.translation import gettext as _

from companies.models import Company
from countries.models import Country


class CompanyForm(forms.ModelForm):
    next = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Company
        fields = [
            "next",
            "name",
            "nip",
            "regon",
            "country",
            "address",
            "zip_code",
            "city",
            "email",
            "phone_number",
        ]

    def __init__(self, *args, current_user, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["country"].queryset = Country.objects.filter(user=current_user)


class CompanyFilterForm(forms.Form):
    name = forms.CharField(label=_("Name"), required=False)
    nip = forms.CharField(required=False)
    regon = forms.CharField(required=False)

    name.widget.attrs.update({"class": "form-control"})
    nip.widget.attrs.update({"class": "form-control"})
    regon.widget.attrs.update({"class": "form-control"})

    def get_filtered_companies(self, companies_list):
        name = self.cleaned_data["name"]
        nip = self.cleaned_data["nip"]
        regon = self.cleaned_data["regon"]

        if name:
            companies_list = companies_list.filter(name__contains=name)
        if nip:
            companies_list = companies_list.filter(nip=nip)
        if regon:
            companies_list = companies_list.filter(regon=regon)

        return companies_list
