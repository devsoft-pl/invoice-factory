from django import forms

from currencies.models import Currency


class CurrencyForm(forms.ModelForm):
    next = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Currency
        fields = ["next", "code"]
        # labels = {"code": "Kod waluty"}
