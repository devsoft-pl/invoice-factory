from django import forms

from accountants.models import Accountant


class AccountantForm(forms.ModelForm):
    class Meta:
        model = Accountant
        fields = ["name", "email"]

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

        for field in self.Meta.fields:
            self.fields[field].widget.attrs["class"] = "form-control"
