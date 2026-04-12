import re

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from companies.managers import MyClientsManager
from countries.models import Country
from users.models import User


class Company(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=100)
    nip = models.CharField(verbose_name=_("NIP"), max_length=20)
    regon = models.CharField(
        verbose_name=_("Regon"),
        max_length=14,
        null=True,
    )
    country = models.ForeignKey(
        Country, verbose_name=_("Country"), on_delete=models.CASCADE, null=True
    )
    address = models.CharField(verbose_name=_("Address"), max_length=100)
    zip_code = models.CharField(verbose_name=_("ZIP Code"), max_length=15)
    city = models.CharField(verbose_name=_("City"), max_length=60)
    email = models.EmailField(verbose_name=_("Email"), null=True, blank=True)
    phone_number = models.CharField(
        verbose_name=_("Phone number"), max_length=20, null=True, blank=True
    )
    user = models.ForeignKey(
        User, verbose_name=_("User"), on_delete=models.CASCADE, null=True
    )
    is_my_company = models.BooleanField(
        verbose_name=_("Is my company"), default=False, editable=False
    )

    objects = models.Manager()
    my_clients = MyClientsManager()

    class Meta:
        verbose_name_plural = _("companies")
        ordering = ["name"]
        unique_together = ["nip", "regon", "user"]

    def __str__(self):
        return self.name

    def _validate_polish_address(self):
        errors = {}
        if self.nip and not re.match(r"^\d{10}$", self.nip):
            errors["nip"] = _("Polish NIP must consist of 10 digits.")
        if self.zip_code and not re.match(r"^\d{2}-\d{3}$", self.zip_code):
            errors["zip_code"] = _("Polish ZIP code must be in the format XX-XXX.")
        return errors

    def _validate_foreign_address(self):
        errors = {}
        if self.nip:
            clean_nip = self.nip.replace(" ", "").replace("-", "")
            if not re.match(r"^[A-Za-z0-9]{4,20}$", clean_nip):
                errors["nip"] = _(
                    "Foreign VAT number contains invalid characters or is incorrect length."
                )
        if self.zip_code:
            if not re.match(r"^[A-Za-z0-9\-\s]{2,15}$", self.zip_code):
                errors["zip_code"] = _(
                    "Foreign ZIP code contains invalid characters or is incorrect length."
                )
        return errors

    def clean(self):
        super().clean()
        errors = {}
        country_name = self.country.country.lower() if self.country else ""

        if country_name == "polska":
            errors = self._validate_polish_address()
        else:
            errors = self._validate_foreign_address()

        if errors:
            raise ValidationError(errors)
