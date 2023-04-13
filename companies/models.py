from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext as _

from countries.models import Country


class Company(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=100)
    nip = models.CharField(verbose_name=_("NIP"), max_length=12)
    regon = models.CharField(verbose_name=_("Regon"), max_length=12, null=True)
    country = models.ForeignKey(
        Country, verbose_name=_("Country"), on_delete=models.CASCADE, null=True
    )
    address = models.CharField(verbose_name=_("Address"), max_length=100)
    zip_code = models.CharField(verbose_name=_("ZIP Code"), max_length=10)
    city = models.CharField(verbose_name=_("City"), max_length=60)
    email = models.EmailField(verbose_name=_("Email"))
    phone_number = models.CharField(
        verbose_name=_("Phone number"), max_length=20, null=True, blank=True
    )
    user = models.ForeignKey(
        User, verbose_name=_("User"), on_delete=models.CASCADE, null=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "companies"
