import decimal

from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext as _
from num2words import num2words

from companies.models import Company
from currencies.models import Currency, ExchangeRate
from persons.models import Person


class Invoice(models.Model):
    INVOICE_SALES = 0
    INVOICE_PURCHASE = 1

    INVOICE_TYPES = (
        (INVOICE_SALES, _("Sales")),
        (INVOICE_PURCHASE, _("Purchase")),
    )

    BANK_TRANSFER = 0
    CASH_PAYMENT = 1

    PAYMENT_METHOD = (
        (BANK_TRANSFER, _("Transfer")),
        (CASH_PAYMENT, _("Cash")),
    )

    WEEKLY = 0
    BIWEEKLY = 1
    MONTHLY = 2
    THREE_MONTH = 3

    FREQUENCY = (
        (WEEKLY, _("Weekly")),
        (BIWEEKLY, _("Biweekly")),
        (MONTHLY, _("Monthly")),
        (THREE_MONTH, _("Three month")),
    )

    invoice_number = models.CharField(
        verbose_name=_("Invoice number"), max_length=30, null=True, blank=True
    )
    invoice_type = models.IntegerField(
        verbose_name=_("Invoice type"), choices=INVOICE_TYPES
    )
    company = models.ForeignKey(
        Company,
        verbose_name=_("Company"),
        on_delete=models.CASCADE,
        related_name="invoice",
    )
    person = models.ForeignKey(Person, verbose_name=_("Person"), on_delete=models.CASCADE, related_name="invoices", null=True, blank=True)
    recurring_frequency = models.IntegerField(
        verbose_name=_("Recurring frequency"), choices=FREQUENCY, null=True, blank=True
    )
    is_recurring = models.BooleanField(verbose_name=_("Recurring"), default=False)
    is_settled = models.BooleanField(verbose_name=_("Settled"), default=False)
    settlement_date = models.DateField(
        verbose_name=_("Settlement date"), null=True, blank=True
    )
    create_date = models.DateField(
        verbose_name=_("Create date"), default=timezone.now, editable=True
    )
    sale_date = models.DateField(verbose_name=_("Sale date"), null=True, blank=True)
    payment_date = models.DateField(
        verbose_name=_("Payment date"), null=True, blank=True
    )
    payment_method = models.IntegerField(
        verbose_name=_("Payment method"), choices=PAYMENT_METHOD, null=True, blank=True
    )
    currency = models.ForeignKey(
        Currency,
        verbose_name=_("Currency"),
        on_delete=models.CASCADE,
        null=True,
        related_name="invoice",
    )
    account_number = models.CharField(
        verbose_name=_("Account number"), max_length=50, null=True, blank=True
    )
    client = models.ForeignKey(
        Company,
        verbose_name=_("Client"),
        on_delete=models.CASCADE,
        related_name="client_invoice",
        null=True,
        blank=True,
    )
    invoice_file = models.FileField(
        verbose_name=_("Invoice file"), null=True, blank=True
    )

    class Meta:
        ordering = ["-sale_date"]
        unique_together = ["invoice_number", "company"]

    def __str__(self):
        return self.invoice_number or f"#{self.id}"

    @property
    def net_amount(self):
        net_sum = 0
        for item in self.items.all():
            net_sum = net_sum + item.net_amount
        return net_sum

    @property
    def tax_amount(self):
        tax_sum = 0
        for item in self.items.all():
            tax_sum = tax_sum + item.tax_amount
        return tax_sum

    @property
    def gross_amount(self):
        gross_sum = decimal.Decimal("0")
        for item in self.items.all():
            gross_sum = gross_sum + item.gross_amount
        return gross_sum

    @property
    def sell_rate_in_pln(self):
        exchange_rate = ExchangeRate.objects.get(
            date=self.sale_date, currency=self.currency
        )
        return exchange_rate.sell_rate

    @property
    def is_sell(self):
        return self.invoice_type == Invoice.INVOICE_SALES

    def get_html_for_pdf(self):
        items = self.items.all()

        template_path = "invoices/pdf_invoice.html"

        gross_whole = self.gross_amount.quantize(decimal.Decimal("1"))
        gross_whole_amount = num2words(gross_whole, lang="pl")
        gross_frac_amount = num2words(int(self.gross_amount - gross_whole), lang="pl")

        context = {
            "invoice": self,
            "items": items,
            "gross_whole_amount": gross_whole_amount,
            "gross_frac_amount": gross_frac_amount,
        }

        html = render_to_string(template_path, context)
        return html
