from django import forms
from django.utils.translation import gettext_lazy as _

from base.validators import rate_validator
from vat_rates.models import VatRate


class VatRateForm(forms.ModelForm):
    def __init__(self, current_user, *args, **kwargs):
        self.current_user = current_user
        super().__init__(*args, **kwargs)

        rate_field: forms.IntegerField = self.fields["rate"]
        rate_field.widget.attrs["class"] = "form-control"
        rate_field.validators = [rate_validator]

    class Meta:
        model = VatRate
        fields = ["rate"]

    def clean_rate(self):
        rate = self.cleaned_data.get("rate")
        vat_rate = VatRate.objects.filter(rate=rate, user=self.current_user)

        if vat_rate.exists():
            raise forms.ValidationError(_("Vat rate already exists"))

        return rate
