from django import forms
from django.contrib.auth.forms import BaseUserCreationForm

from users.models import User


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password"]


class UserCreationForm(BaseUserCreationForm):
    class Meta:
        model = User
        fields = ["email", "password1", "password2"]
