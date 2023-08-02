from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext as _


class Currency(models.Model):
    code = models.CharField(verbose_name=_("Code"), max_length=10)
    user = models.ForeignKey(
        User, verbose_name=_("User"), on_delete=models.CASCADE, null=True
    )

    def __str__(self):
        return self.code

    class Meta:
        verbose_name_plural = _("currencies")
        ordering = ["code"]


class ExchangeRate(models.Model):
    buy_rate = models.DecimalField(
        verbose_name=_("Buy rate"), max_digits=5, decimal_places=4, default=0
    )
    sell_rate = models.DecimalField(
        verbose_name=_("Sell rate"), max_digits=5, decimal_places=4, default=0
    )
    date = models.DateField(verbose_name=_("Date"))
    currency = models.ForeignKey(
        Currency, verbose_name=_("Currency"), on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.currency.code}: {self.date}"
