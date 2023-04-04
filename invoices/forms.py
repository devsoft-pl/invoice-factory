from django import forms

from invoices.models import (
    VatRate,
    Currency,
    Country,
    Company,
    Invoice
)


class VatRateForm(forms.ModelForm):
    class Meta:
        model = VatRate
        fields = ["rate"]


class CurrencyForm(forms.ModelForm):

    class Meta:
        model = Currency
        fields = ["code"]


class CountryForm(forms.ModelForm):

    class Meta:
        model = Country
        fields = ["country"]

class CompanyForm(forms.ModelForm):

    class Meta:
        model = Company
        fields = ["name", "nip", "regon", "country", "address", "zip_code", "city", "email", "phone_number"]


class InvoiceForm(forms.ModelForm):

    class Meta:
        model = Invoice
        fields = ["invoice_number", "invoice_type", "company", "recurring_frequency", "is_recurring", "create_date", "sale_date", "payment_date", "payment_method", "currency", "account_number"]