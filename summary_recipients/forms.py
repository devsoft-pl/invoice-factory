from django import forms

from summary_recipients.models import SummaryRecipient


class SummaryRecipientForm(forms.ModelForm):
    class Meta:
        model = SummaryRecipient
        fields = [
            "description",
            "day",
            "email",
            "settlement_types",
            "final_call"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.Meta.fields:
            self.fields[field].widget.attrs["class"] = "form-control"
