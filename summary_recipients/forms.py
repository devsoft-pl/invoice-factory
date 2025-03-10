from django import forms
from django.utils.translation import gettext_lazy as _

from base.validators import max_day_validator
from summary_recipients.models import SummaryRecipient

LAST_DAYS_OF_MONTH = [28, 29, 30, 31]


class SummaryRecipientForm(forms.ModelForm):
    class Meta:
        model = SummaryRecipient
        fields = [
            "description",
            "day",
            "email",
            "settlement_types",
            "final_call",
            "is_last_day",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.Meta.fields:
            if field in ["final_call", "is_last_day"]:
                continue
            self.fields[field].widget.attrs["class"] = "form-control"

        day_field: forms.IntegerField = self.fields["day"]
        day_field.validators = [max_day_validator]

    def clean_day(self):
        day = self.cleaned_data.get("day")
        is_last_day = self.data.get("is_last_day")

        if is_last_day and day not in LAST_DAYS_OF_MONTH:
            raise forms.ValidationError(_("This field is not last day of month."))

        return day
