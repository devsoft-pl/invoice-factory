from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext as _


class Country(models.Model):
    country = models.CharField(verbose_name=_("Country"), max_length=30)
    user = models.ForeignKey(
        User, verbose_name=_("User"), on_delete=models.CASCADE, null=True
    )
    is_my_country = models.BooleanField(
        verbose_name=_("Is my country"), default=False, editable=False
    )

    def __str__(self):
        return self.country

    class Meta:
        verbose_name_plural = "countries"
