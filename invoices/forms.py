from django import forms

from invoices.models import VatRate


class VatRateForm(forms.ModelForm):
    class Meta:
        model = VatRate
        fields = ["rate"]
