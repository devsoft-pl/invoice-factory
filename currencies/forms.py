from django import forms
from django.utils.translation import gettext as _

from currencies.models import Currency


class CurrencyForm(forms.ModelForm):
    next = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    class Meta:
        model = Currency
        fields = ["next", "code"]

    def clean_code(self):
        code = self.cleaned_data.get("code")

        currency = Currency.objects.filter(code=code, user=self.user)
        if currency.exists():
            raise forms.ValidationError(_("Currency already exists"))

        return code
