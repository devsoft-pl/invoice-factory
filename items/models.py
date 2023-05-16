import decimal

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext as _

from invoices.models import Invoice
from vat_rates.models import VatRate


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
    net_price = models.DecimalField(
        verbose_name=_("Net price"), max_digits=9, decimal_places=2
    )
    vat = models.ForeignKey(
        VatRate, verbose_name=_("Vat"), on_delete=models.CASCADE, related_name="item"
    )
    user = models.ForeignKey(
        User, verbose_name=_("User"), on_delete=models.CASCADE, null=True
    )
    is_my_item = models.BooleanField(
        verbose_name=_("Is my item"), default=False, editable=False
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
        return decimal.Decimal(self.net_amount + self.tax_amount)
