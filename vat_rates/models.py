from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import User


class VatRate(models.Model):
    rate = models.PositiveIntegerField(
        verbose_name=_("Rate"),
    )
    user = models.ForeignKey(
        User, verbose_name=_("User"), on_delete=models.CASCADE, null=True
    )

    def __str__(self):
        return str(self.rate)

    class Meta:
        verbose_name_plural = _("vat rates")
        ordering = ["rate"]
        unique_together = ["rate", "user"]
