from django import forms

from base.validators import max_day_validator
from summary_recipients.models import SummaryRecipient


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
