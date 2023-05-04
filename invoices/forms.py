from django import forms
from django.utils.translation import gettext as _

from companies.models import Company
from currencies.models import Currency
from invoices.models import Invoice


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            "invoice_number",
            "invoice_type",
            "company",
            "create_date",
            "sale_date",
            "payment_date",
            "payment_method",
            "currency",
            "account_number",
        ]

    def __init__(self, *args, current_user, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["company"].queryset = Company.objects.filter(user=current_user)
        self.fields["currency"].queryset = Currency.objects.filter(user=current_user)


class InvoiceFilterForm(forms.Form):
    invoice_number = forms.CharField(label=_("Invoice number"), required=False)
    invoice_type = forms.ChoiceField(
        label=_("Invoice type"), required=False, choices=Invoice.INVOICE_TYPES
    )
    company = forms.CharField(label=_("Company"), required=False)
