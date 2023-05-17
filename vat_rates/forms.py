from django import forms

from vat_rates.models import VatRate


class VatRateForm(forms.ModelForm):
    next = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = VatRate
        fields = ["next", "rate"]
