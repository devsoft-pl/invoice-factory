from django import forms

from companies.models import Company


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
        labels = {
            "name": "Nazwa firmy",
            "nip": "Nip",
            "regon": "Regon",
            "country": "Kraj",
            "address": "Adres",
            "zip_code": "Kod pocztowy",
            "city": "Miasto",
            "email": "Email",
            "phone_number": "Numer telefonu",
        }
