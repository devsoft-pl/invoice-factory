from django import forms

from invoices.models import (
    VatRate,
    Currency,
    Country
)


class VatRateForm(forms.ModelForm):
    class Meta:
        model = VatRate
        fields = ["rate"]


class CurrencyForm(forms.ModelForm):

    class Meta:
        model = Currency
        fields = ["code"]


class CountryForm(forms.ModelForm):

    class Meta:
        model = Country
        fields = ["country"]