from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext as _


class VatRate(models.Model):
    rate = models.PositiveIntegerField(verbose_name=_("Rate"), unique=True)
    user = models.ForeignKey(
        User, verbose_name=_("User"), on_delete=models.CASCADE, null=True
    )

    def __str__(self):
        return str(self.rate)

    class Meta:
        ordering = ["rate"]
