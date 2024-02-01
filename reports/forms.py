from django import forms
from django.utils.translation import gettext as _

from invoices.models import Year


class ReportFilterForm(forms.Form):
    NETTO = "netto"
    GROSS = "gross"
    ALL = "all"

    REVENUES = ((ALL, _("All")), (NETTO, _("Netto")), (GROSS, _("Gross")))

    revenue_type = forms.ChoiceField(
        label=_("Revenue type"), required=False, choices=REVENUES
    )
    year = forms.ModelChoiceField(
        queryset=Year.objects.all(), label=_("Year"), required=False, empty_label=None
    )

    revenue_type.widget.attrs.update({"class": "form-select"})
    year.widget.attrs.update({"class": "form-select"})
