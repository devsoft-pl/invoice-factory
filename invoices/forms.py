from django import forms

from invoices.models import Company, Country, Currency, Invoice, Item, VatRate


class VatRateForm(forms.ModelForm):
    class Meta:
        model = VatRate
        fields = ["rate"]


class CurrencyForm(forms.ModelForm):
    next = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Currency
        fields = [
            "next",
            "code"]
        labels = {
            "code": "Kod kraju"
        }


class CountryForm(forms.ModelForm):
    class Meta:
        model = Country
        fields = ["country"]


class CompanyForm(forms.ModelForm):
    next = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Company
        fields = [
            "next",
            "name",
            "nip",
            "regon",
            "country",
            "address",
            "zip_code",
            "city",
            "email",
            "phone_number",
        ]
        labels = {
            "name": "Nazwa firmy",
            "nip": "Nip",
            "regon": "Regon",
            "country": "Kraj",
            "address": "Adres",
            "zip_code": "Kod pocztowy",
            "city": "Miasto",
            "email": "Email",
            "phone_number": "Numer telefonu",
        }

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


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["name", "pkwiu", "amount", "net_price", "vat"]
