from django import forms

from invoices.models import (
    VatRate,
    Currency
)


class VatRateForm(forms.ModelForm):
    class Meta:
        model = VatRate
        fields = ["rate"]


class CurrencyForm(forms.ModelForm):

    class Meta:
        model = Currency
        fields = ["Currency"]

