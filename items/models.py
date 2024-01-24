import decimal

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

    class Meta:
        ordering = ["vat"]

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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        net_amount = self.invoice.calculate_net_amount()
        self.invoice.net_amount = net_amount

        gross_amount = self.invoice.calculate_gross_amount()
        self.invoice.gross_amount = gross_amount

        self.invoice.save()

    def delete(self, *args, **kwargs):
        deleted_objects = super().delete(*args, **kwargs)

        net_amount = self.invoice.calculate_net_amount()
        self.invoice.net_amount = net_amount

        gross_amount = self.invoice.calculate_gross_amount()
        self.invoice.gross_amount = gross_amount

        self.invoice.save()

        return deleted_objects
