from django import forms
from django.utils.translation import gettext_lazy as _

from base.validators import currency_validator
from currencies.models import Currency


class CurrencyForm(forms.ModelForm):
    def __init__(self, current_user, *args, **kwargs):
        self.current_user = current_user
        super().__init__(*args, **kwargs)

        currency_field: forms.CharField = self.fields["code"]
        currency_field.widget.attrs["class"] = "form-control"
        currency_field.validators = [currency_validator]

    class Meta:
        model = Currency
        fields = ["code"]

    def clean_code(self):
        code = self.cleaned_data.get("code")
        currency = Currency.objects.filter(code=code, user=self.current_user)

        if currency.exists():
            raise forms.ValidationError(_("Currency already exists"))

        return code
