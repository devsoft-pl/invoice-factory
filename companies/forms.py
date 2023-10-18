from django import forms
from django.core.validators import RegexValidator
from django.utils.translation import gettext as _

from companies.models import Company, SummaryRecipient
from countries.models import Country

nip_validator = RegexValidator(
    r"^[0-9a-zA-Z]{8,16}$",
    _("Enter the tax ID without special characters with minimum 8 character"),
)

regon_validator = RegexValidator(
    r"^([0-9]{9}|[0-9]{14})$",
    _("Enter regon in numbers only with minimum 9 character"),
)

zip_code_validator = RegexValidator(
    r"^[0-9]{2}-[0-9]{3}$", _("Zip code in numbers only in format xx-xxx")
)

city_validator = RegexValidator(r"^[a-zA-Z ]+$", _("Enter the city in letters only"))

phone_number_validator = RegexValidator(
    r"^[0-9]{9,}$", _("Enter phone number with 9 numbers only")
)


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

    def __init__(self, current_user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_user = current_user
        self.fields["country"].queryset = Country.objects.filter(
            user=current_user
        ).order_by("country")

        for field in self.Meta.fields:
            self.fields[field].widget.attrs["class"] = "form-control"

        self.fields["nip"].validators = [nip_validator]
        self.fields["regon"].validators = [regon_validator]
        self.fields["zip_code"].validators = [zip_code_validator]
        self.fields["city"].validators = [city_validator]
        self.fields["phone_number"].validators = [phone_number_validator]

    def clean_nip(self):
        nip = self.cleaned_data.get("nip")
        company = Company.objects.filter(nip=nip, user=self.current_user)

        if self.instance.pk:
            company = company.exclude(pk=self.instance.pk)

        if company.exists():
            raise forms.ValidationError(_("Nip already exists"))

        return nip

    def clean_regon(self):
        regon = self.cleaned_data.get("regon")
        company = Company.objects.filter(regon=regon, user=self.current_user)

        if self.instance.pk:
            company = company.exclude(pk=self.instance.pk)

        if company.exists():
            raise forms.ValidationError(_("Regon already exists"))

        return regon


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


class SummaryRecipientForm(forms.ModelForm):
    class Meta:
        model = SummaryRecipient
        fields = [
            "description",
            "day",
            "email",
            "settlement_types",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.Meta.fields:
            self.fields[field].widget.attrs["class"] = "form-control"
