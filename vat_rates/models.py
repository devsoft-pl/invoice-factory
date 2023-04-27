from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext as _


class VatRate(models.Model):
    rate = models.PositiveIntegerField(verbose_name=_("Rate"))
    user = models.ForeignKey(
        User, verbose_name=_("User"), on_delete=models.CASCADE, null=True
    )
    is_my_vat = models.BooleanField(
        verbose_name=_("Is my vat"), default=False, editable=False
    )

    def __str__(self):
        return str(self.rate)

    class Meta:
        ordering = ["rate"]
