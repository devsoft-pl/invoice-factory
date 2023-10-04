from django import forms
from django.core.validators import MaxValueValidator
from django.utils.translation import gettext as _

from vat_rates.models import VatRate

rate_validator = MaxValueValidator(99)


class VatRateForm(forms.ModelForm):
    next = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

        rate_field: forms.IntegerField = self.fields["rate"]
        rate_field.widget.attrs["class"] = "form-control"
        rate_field.widget.attrs["max"] = "99"
        rate_field.validators = [rate_validator]

    class Meta:
        model = VatRate
        fields = ["next", "rate"]

    def clean_rate(self):
        rate = self.cleaned_data.get("rate")
        vat_rate = VatRate.objects.filter(rate=rate, user=self.user)

        if vat_rate.exists():
            raise forms.ValidationError(_("Vat rate already exists"))

        return rate
