from django import forms

from vat_rates.models import VatRate


class VatRateForm(forms.ModelForm):
    class Meta:
        model = VatRate
        fields = ["rate"]
        labels ={
            "rate": "Stawka vat"
        }