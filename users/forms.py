import time

from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    BaseUserCreationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.core.signing import TimestampSigner
from django.utils.translation import gettext_lazy as _

from users.models import User


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.Meta.fields:
            self.fields[field].widget.attrs["class"] = "form-control"


class UserCreationForm(BaseUserCreationForm):
    honeypot = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label=_("Leave this field empty"),
    )
    timestamp = forms.CharField(
        required=True,
        widget=forms.HiddenInput(),
    )

    class Meta:
        model = User
        fields = ["email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["timestamp"].initial = TimestampSigner().sign(str(time.time()))

        for field in ["email", "password1", "password2"]:
            self.fields[field].widget.attrs["class"] = "form-control"

    def clean(self):
        cleaned_data = super().clean()
        honeypot = cleaned_data.get("honeypot")
        timestamp = cleaned_data.get("timestamp")

        if honeypot:
            raise forms.ValidationError(_("Registration not allowed for bots."))

        if not timestamp:
            raise forms.ValidationError(_("Invalid form submission."))

        try:
            ts = TimestampSigner().unsign(timestamp, max_age=3600)  # 1 hour max
            submitted_time = float(ts)
        except Exception:
            raise forms.ValidationError(_("Invalid form submission."))

        if time.time() - submitted_time < 3:  # Must take at least 3 seconds
            raise forms.ValidationError(_("Registration too fast, possible bot."))

        return cleaned_data


class PasswordChangeUserForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ["old_password", "new_password1", "new_password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.Meta.fields:
            self.fields[field].widget.attrs["class"] = "form-control"


class PasswordResetUserForm(PasswordResetForm):

    class Meta:
        model = User
        fields = ["email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.Meta.fields:
            self.fields[field].widget.attrs["class"] = "form-control"


class PasswordResetConfirmUserForm(SetPasswordForm):

    class Meta:
        model = User
        fields = ["new_password1", "new_password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.Meta.fields:
            self.fields[field].widget.attrs["class"] = "form-control"


class LoginUserForm(AuthenticationForm):

    class Meta:
        model = User
        fields = ["username", "password"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.Meta.fields:
            self.fields[field].widget.attrs["class"] = "form-control"
