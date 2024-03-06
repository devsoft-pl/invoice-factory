from django import forms
from django.utils.translation import gettext as _

from base.validators import (account_number_validator,
                             correction_invoice_number_validator,
                             invoice_number_validator)
from companies.models import Company
from currencies.models import Currency
from invoices.models import CorrectionInvoiceRelation, Invoice
from persons.models import Person


class InvoiceSellForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            "invoice_number",
            "company",
            "client",
            "create_date",
            "sale_date",
            "payment_date",
            "payment_method",
            "currency",
            "account_number",
            "is_recurring",
            "is_last_day",
            "is_paid",
        ]

    def __init__(self, *args, current_user, create_correction=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_user = current_user
        self.fields["company"].queryset = Company.objects.filter(
            user=current_user, is_my_company=True
        ).order_by("name")
        self.fields["client"].queryset = Company.objects.filter(
            user=current_user, is_my_company=False
        ).order_by("name")
        self.fields["currency"].queryset = Currency.objects.filter(
            user=current_user
        ).order_by("code")

        if (
            not create_correction
            and not CorrectionInvoiceRelation.objects.filter(
                correction_invoice=self.instance
            ).exists()
        ):
            invoice_number_field: forms.CharField = self.fields["invoice_number"]
            invoice_number_field.validators = [invoice_number_validator]
        else:
            invoice_number_field: forms.CharField = self.fields["invoice_number"]
            invoice_number_field.validators = [correction_invoice_number_validator]

        account_number_field: forms.CharField = self.fields["account_number"]
        account_number_field.validators = [account_number_validator]

        if not self.data or self.data.get("payment_method") == str(
            Invoice.CASH_PAYMENT
        ):
            self.fields["account_number"].required = False
        else:
            self.fields["account_number"].required = True

        for field in self.Meta.fields:
            if field == "is_paid":
                continue
            if field == "is_recurring":
                continue
            if field == "is_last_day":
                continue
            self.fields[field].widget.attrs["class"] = "form-control"

        self.fields["create_date"].widget.attrs["autocomplete"] = "off"
        self.fields["sale_date"].widget.attrs["autocomplete"] = "off"
        self.fields["payment_date"].widget.attrs["autocomplete"] = "off"

    def clean_invoice_number(self):
        invoice_number = self.cleaned_data.get("invoice_number")
        is_recurring = self.data.get("is_recurring")

        if not is_recurring and not invoice_number:
            raise forms.ValidationError(_("This field is required."))

        invoice = Invoice.objects.filter(
            invoice_number=invoice_number,
            company__user=self.current_user,
        )

        if self.instance.pk:
            invoice = invoice.exclude(pk=self.instance.pk)

        if invoice.exists():
            raise forms.ValidationError(_("Invoice number already exists"))

        return invoice_number


class InvoiceSellPersonForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            "invoice_number",
            "company",
            "person",
            "create_date",
            "sale_date",
            "payment_date",
            "payment_method",
            "currency",
            "account_number",
            "is_recurring",
            "is_last_day",
            "is_paid",
        ]

    def __init__(self, current_user, create_correction=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_user = current_user

        self.fields["company"].queryset = Company.objects.filter(
            user=current_user, is_my_company=True
        ).order_by("name")
        self.fields["person"].queryset = Person.objects.filter(user=current_user)
        self.fields["currency"].queryset = Currency.objects.filter(
            user=current_user
        ).order_by("code")

        if (
            not create_correction
            and not CorrectionInvoiceRelation.objects.filter(
                correction_invoice=self.instance
            ).exists()
        ):
            invoice_number_field: forms.CharField = self.fields["invoice_number"]
            invoice_number_field.validators = [invoice_number_validator]
        else:
            invoice_number_field: forms.CharField = self.fields["invoice_number"]
            invoice_number_field.validators = [correction_invoice_number_validator]

        account_number_field: forms.CharField = self.fields["account_number"]
        account_number_field.validators = [account_number_validator]

        if not self.data or self.data.get("payment_method") == str(
            Invoice.CASH_PAYMENT
        ):
            self.fields["account_number"].required = False
        else:
            self.fields["account_number"].required = True

        for field in self.Meta.fields:
            if field == "is_paid":
                continue
            if field == "is_recurring":
                continue
            if field == "is_last_day":
                continue
            self.fields[field].widget.attrs["class"] = "form-control"

        self.fields["create_date"].widget.attrs["autocomplete"] = "off"
        self.fields["sale_date"].widget.attrs["autocomplete"] = "off"
        self.fields["payment_date"].widget.attrs["autocomplete"] = "off"

    def clean_invoice_number(self):
        invoice_number = self.cleaned_data.get("invoice_number")
        invoice = Invoice.objects.filter(
            invoice_number=invoice_number,
            company__user=self.current_user,
        )

        if self.instance.pk:
            invoice = invoice.exclude(pk=self.instance.pk)

        if invoice.exists():
            raise forms.ValidationError(_("Invoice number already exists"))

        return invoice_number


class InvoiceRecurringForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            "is_recurring",
        ]


class InvoiceBuyForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            "invoice_number",
            "company",
            "sale_date",
            "payment_date",
            "settlement_date",
            "invoice_file",
            "is_paid",
        ]

    def __init__(self, *args, current_user, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_user = current_user
        self.fields["company"].queryset = Company.objects.filter(
            user=current_user, is_my_company=True
        ).order_by("name")

        for field in self.Meta.fields:
            if field == "is_paid":
                continue
            self.fields[field].widget.attrs["class"] = "form-control"
            self.fields[field].required = True

        self.fields["sale_date"].widget.attrs["autocomplete"] = "off"
        self.fields["payment_date"].widget.attrs["autocomplete"] = "off"
        self.fields["settlement_date"].widget.attrs["autocomplete"] = "off"

    def clean_invoice_number(self):
        invoice_number = self.cleaned_data.get("invoice_number")
        invoice = Invoice.objects.filter(
            invoice_number=invoice_number,
            company__user=self.current_user,
        )
        if self.instance.pk:
            invoice = invoice.exclude(pk=self.instance.pk)

        if invoice.exists():
            raise forms.ValidationError(_("Invoice number already exists"))

        return invoice_number


class InvoiceFilterForm(forms.Form):
    invoice_number = forms.CharField(label=_("Invoice number"), required=False)
    invoice_type = forms.ChoiceField(
        label=_("Invoice type"), required=False, choices=Invoice.INVOICE_TYPES
    )
    client = forms.CharField(label=_("Client"), required=False)
    company = forms.CharField(label=_("Company"), required=False)

    invoice_number.widget.attrs.update({"class": "form-control"})
    invoice_type.widget.attrs.update({"class": "form-select"})
    client.widget.attrs.update({"class": "form-control"})
    company.widget.attrs.update({"class": "form-control"})

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
            invoices_list = invoices_list.filter(client__name__icontains=client)
        if company:
            invoices_list = invoices_list.filter(company__name__icontains=company)

        return invoices_list
