from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _

from companies.models import Company


class VatRate(models.Model):
    rate = models.PositiveIntegerField(verbose_name=_("Rate"), unique=True)
    user = models.ForeignKey(
        User, verbose_name=_("User"), on_delete=models.CASCADE, null=True
    )

    def __str__(self):
        return str(self.rate)

    class Meta:
        ordering = ["rate"]


class Currency(models.Model):
    code = models.CharField(verbose_name=_("Code"), max_length=10, unique=True)
    user = models.ForeignKey(
        User, verbose_name=_("User"), on_delete=models.CASCADE, null=True
    )

    def __str__(self):
        return self.code

    class Meta:
        verbose_name_plural = "currencies"


class Invoice(models.Model):
    INVOICE_SALES = 0
    INVOICE_PURCHASE = 1

    INVOICE_TYPES = (
        (INVOICE_SALES, "Sales"),
        (INVOICE_PURCHASE, "Purchase"),
    )

    BANK_TRANSFER = 0
    CASH_PAYMENT = 1

    PAYMENT_METHOD = (
        (BANK_TRANSFER, "Transfer"),
        (CASH_PAYMENT, "Cash"),
    )

    WEEKLY = 0
    BIWEEKLY = 1
    MONTHLY = 2
    THREE_MONTH = 3

    FREQUENCY = (
        (WEEKLY, "Weekly"),
        (BIWEEKLY, "Biweekly"),
        (MONTHLY, "Monthly"),
        (THREE_MONTH, "Three month"),
    )

    user = models.ForeignKey(
        User, verbose_name=_("User"), on_delete=models.CASCADE, null=True
    )
    invoice_number = models.CharField(verbose_name=_("Invoice number"), max_length=30)
    invoice_type = models.IntegerField(
        verbose_name=_("Invoice type"), choices=INVOICE_TYPES
    )
    company = models.ForeignKey(
        Company,
        verbose_name=_("Company"),
        on_delete=models.CASCADE,
        related_name="invoice",
    )
    recurring_frequency = models.IntegerField(
        verbose_name=_("Recurring_frequency"), choices=FREQUENCY, null=True, blank=True
    )
    is_recurring = models.BooleanField(verbose_name=_("Recurring"), default=False)
    create_date = models.DateField(
        verbose_name=_("Create date"), default=timezone.now, editable=True
    )
    sale_date = models.DateField(
        verbose_name=_("Sale date"), default=timezone.now, editable=True
    )
    payment_date = models.DateField(
        verbose_name=_("Payment date"), default=timezone.now, editable=True
    )
    payment_method = models.IntegerField(
        verbose_name=_("Payment method"), choices=PAYMENT_METHOD
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
        gross_sum = 0
        for item in self.items.all():
            gross_sum = gross_sum + item.gross_amount
        return gross_sum


class Item(models.Model):
    invoice = models.ForeignKey(
        Invoice,
        verbose_name=_("Invoice"),
        on_delete=models.CASCADE,
        related_name="items",
    )
    name = models.CharField(verbose_name=_("Name"), max_length=255)
    pkwiu = models.CharField(verbose_name=_("PWKiU"), max_length=50, null=True)
    amount = models.PositiveIntegerField(verbose_name=_("Amount"))
    net_price = models.PositiveIntegerField(verbose_name=_("Net price"))
    vat = models.ForeignKey(
        VatRate, verbose_name=_("Vat"), on_delete=models.CASCADE, related_name="item"
    )
    user = models.ForeignKey(
        User, verbose_name=_("User"), on_delete=models.CASCADE, null=True
    )

    def __str__(self):
        return self.name

    @property
    def net_amount(self):
        return self.amount * self.net_price

    @property
    def tax_amount(self):
        return (self.net_amount * self.vat.rate) / 100

    @property
    def gross_amount(self):
        return self.net_amount + self.tax_amount
