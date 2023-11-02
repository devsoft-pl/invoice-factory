from django import forms
from django.core.validators import RegexValidator
from django.utils.translation import gettext as _

from accountants.models import Accountant

phone_number_validator = RegexValidator(
    r"^[0-9]{9,}$", _("Enter phone number with 9 numbers only")
)


class AccountantForm(forms.ModelForm):
    class Meta:
        model = Accountant
        fields = ["name", "email", "phone_number"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.Meta.fields:
            self.fields[field].widget.attrs["class"] = "form-control"

        self.fields["phone_number"].validators = [phone_number_validator]
