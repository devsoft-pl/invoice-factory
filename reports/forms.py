from django import forms
from django.utils.translation import gettext_lazy as _

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
        queryset=Year.objects.none(),  # Zmieniamy na pusty queryset
        label=_("Year"),
        required=False,
        empty_label=None,
    )

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["year"].queryset = Year.objects.filter(user=user)

        self.fields["revenue_type"].widget.attrs.update({"class": "form-select"})
        self.fields["year"].widget.attrs.update({"class": "form-select"})
