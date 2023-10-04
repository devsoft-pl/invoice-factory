from django import forms
from django.contrib.auth.forms import BaseUserCreationForm
from django.core.validators import RegexValidator
from django.utils.translation import gettext as _

from users.models import User

first_name_validator = RegexValidator(
    r"^[a-zA-Z ]+$",
    _("Enter first name in letters only"),
)
last_name_validator = RegexValidator(
    r"^[a-zA-Z ]+$",
    _("Enter last name in letters only"),
)


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        first_name_field: forms.CharField = self.fields["first_name"]
        first_name_field.validators = [first_name_validator]

        last_name_field: forms.CharField = self.fields["last_name"]
        last_name_field.validators = [last_name_validator]

        for field in self.Meta.fields:
            self.fields[field].widget.attrs["class"] = "form-control"


class UserCreationForm(BaseUserCreationForm):
    class Meta:
        model = User
        fields = ["email", "password1", "password2"]
