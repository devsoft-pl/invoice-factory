from django import forms

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
            "recurring_frequency",
            "is_recurring",
            "create_date",
            "sale_date",
            "payment_date",
            "payment_method",
            "currency",
            "account_number",
        ]
        labels = {
            "invoice_number": "Numer faktury",
            "invoice_type": "Typ faktury",
            "company": "Nazwa firmy",
            "recurring_frequency": "Częstotliwość faktury",
            "is_recurring": "Czy powtarzalna",
            "create_date": "Data utworzenia",
            "sale_date": "Data sprzedaży",
            "payment_date": "Data płatności",
            "payment_method": "Forma płatności",
            "currency": "Waluta",
            "account_number": "Numer konta",
        }

    def __init__(self, *args, current_user, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["company"].queryset = Company.objects.filter(user=current_user)
        self.fields["currency"].queryset = Currency.objects.filter(user=current_user)
