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
            "client",
            "create_date",
            "sale_date",
            "payment_date",
            "payment_method",
            "currency",
            "account_number",
        ]

    def __init__(self, *args, current_user, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["company"].queryset = Company.objects.filter(
            user=current_user, is_my_company=True
        )
        self.fields["client"].queryset = Company.objects.filter(
            user=current_user, is_my_company=False
        )
        self.fields["currency"].queryset = Currency.objects.filter(user=current_user)


class InvoiceFilterForm(forms.Form):
    invoice_number = forms.CharField(label=_("Invoice number"), required=False)
    invoice_type = forms.ChoiceField(
        label=_("Invoice type"), required=False, choices=Invoice.INVOICE_TYPES
    )
    client = forms.CharField(label=_("Client"), required=False)
    company = forms.CharField(label=_("Company"), required=False)

    def get_filtered_invoices(self, invoices_list):
        invoice_number = self.cleaned_data["invoice_number"]
        invoice_type = self.cleaned_data["invoice_type"]
        company = self.cleaned_data["company"]
        client = self.cleaned_data["client"]

        if invoice_number:
            invoices_list = invoices_list.filter(
                invoice_number__contains=invoice_number
            )
        if invoice_type:
            invoices_list = invoices_list.filter(invoice_type=invoice_type)
        if client:
            invoices_list = invoices_list.filter(client__name__contains=client)
        if company:
            invoices_list = invoices_list.filter(company__name__contains=company)

        return invoices_list
