from django import forms

from accountants.models import Accountant


class AccountantForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    class Meta:
        model = Accountant
        fields = ["name", "email"]
