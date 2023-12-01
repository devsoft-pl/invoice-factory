from django import forms

from accountants.models import Accountant
from base.validators import phone_number_validator


class AccountantForm(forms.ModelForm):
    class Meta:
        model = Accountant
        fields = ["name", "email", "phone_number"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.Meta.fields:
            self.fields[field].widget.attrs["class"] = "form-control"

        self.fields["phone_number"].validators = [phone_number_validator]
