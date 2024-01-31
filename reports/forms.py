from django import forms
from django.utils.translation import gettext as _


class ReportFilterForm(forms.Form):
    NETTO = "netto"
    GROSS = "gross"
    ALL = "all"

    REVENUES = ((ALL, _("All")), (NETTO, _("Netto")), (GROSS, _("Gross")))

    revenue_type = forms.ChoiceField(
        label=_("Revenue type"), required=False, choices=REVENUES
    )

    revenue_type.widget.attrs.update({"class": "form-select"})

