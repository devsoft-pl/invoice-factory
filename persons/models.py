from django.db import models
from django.utils.translation import gettext as _

from countries.models import Country


class Person(models.Model):
    first_name = models.CharField(_("First name"), max_length=75)
    last_name = models.CharField(_("Last name"), max_length=75)
    address = models.CharField(verbose_name=_("Address"), max_length=100)
    zip_code = models.CharField(verbose_name=_("ZIP Code"), max_length=10)
    city = models.CharField(verbose_name=_("City"), max_length=60)
    country = models.ForeignKey(
        Country, verbose_name=_("Country"), on_delete=models.CASCADE, null=True
    )
    email = models.EmailField(verbose_name=_("Email"))
    phone_number = models.CharField(verbose_name=_("Phone number"), max_length=20)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


