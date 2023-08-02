from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext as _


class Currency(models.Model):
    code = models.CharField(verbose_name=_("Code"), max_length=10)
    exchange_rate = models.DecimalField(verbose_name=_("Exchange rate"), max_digits=5, decimal_places=4, default=0)
    user = models.ForeignKey(
        User, verbose_name=_("User"), on_delete=models.CASCADE, null=True
    )

    def __str__(self):
        return self.code

    class Meta:
        verbose_name_plural = _("currencies")
        ordering = ["code"]
