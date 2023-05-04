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
