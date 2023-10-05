from django import forms
from django.core.validators import RegexValidator
from django.utils.translation import gettext as _

from currencies.models import Currency

currency_validator = RegexValidator(
    r"^[a-zA-Z]{3}$", _("Enter country three letter code")
)


class CurrencyForm(forms.ModelForm):
    next = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

        currency_field: forms.CharField = self.fields["code"]
        currency_field.widget.attrs["class"] = "form-control"
        currency_field.validators = [currency_validator]

    class Meta:
        model = Currency
        fields = ["next", "code"]

    def clean_code(self):
        code = self.cleaned_data.get("code")
        currency = Currency.objects.filter(code=code, user=self.user)

        if currency.exists():
            raise forms.ValidationError(_("Currency already exists"))

        return code
