from django.db import models, transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext as _

from users.models import User


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
        unique_together = ["code", "user"]

    @property
    def last_exchange_rate(self):
        try:
            last_exchange_rate = self.exchange_rates.order_by("-date")[0]
            return last_exchange_rate
        except IndexError:
            return None


@receiver(post_save, sender=Currency)
def create_exchange_rates(sender, instance: Currency, created=False, **kwargs):
    from currencies.tasks import get_exchange_rate_for_currency

    if created:
        transaction.on_commit(
            lambda: get_exchange_rate_for_currency.apply_async(args=[instance.id])
        )


class ExchangeRate(models.Model):
    buy_rate = models.DecimalField(
        verbose_name=_("Buy rate"), max_digits=5, decimal_places=4, default=0
    )
    sell_rate = models.DecimalField(
        verbose_name=_("Sell rate"), max_digits=5, decimal_places=4, default=0
    )
    date = models.DateField(verbose_name=_("Date"))
    currency = models.ForeignKey(
        Currency,
        verbose_name=_("Currency"),
        on_delete=models.CASCADE,
        related_name="exchange_rates",
    )

    def __str__(self):
        return f"{self.currency.code}: {self.date}"
