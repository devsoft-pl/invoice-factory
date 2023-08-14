from django import forms
from django.utils.translation import gettext as _

from vat_rates.models import VatRate


class VatRateForm(forms.ModelForm):
    next = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields["rate"].widget.attrs["class"] = "form-control"

    class Meta:
        model = VatRate
        fields = ["next", "rate"]

    def clean_rate(self):
        rate = self.cleaned_data.get("rate")
        vat_rate = VatRate.objects.filter(rate=rate, user=self.user)

        if vat_rate.exists():
            raise forms.ValidationError(_("Vat rate already exists"))

        return rate
