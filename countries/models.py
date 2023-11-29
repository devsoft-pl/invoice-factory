from django.db import models
from django.utils.translation import gettext as _

from users.models import User


class Country(models.Model):
    country = models.CharField(verbose_name=_("Country"), max_length=30)
    user = models.ForeignKey(
        User, verbose_name=_("User"), on_delete=models.CASCADE, null=True
    )

    class Meta:
        verbose_name_plural = _("countries")
        ordering = ["country"]
        unique_together = ["country", "user"]

    def __str__(self):
        return self.country.capitalize()


