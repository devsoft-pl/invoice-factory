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

    def get_filtered_reports(self, reports_list):
        revenue_type = self.cleaned_data["revenue_type"]

        if revenue_type:
            reports_list = reports_list.filter(revenue_type=revenue_type)

        return reports_list
