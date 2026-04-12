import re

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from countries.models import Country
from users.models import User


class Person(models.Model):
    first_name = models.CharField(_("First name"), max_length=75)
    last_name = models.CharField(_("Last name"), max_length=75)
    nip = models.CharField(verbose_name=_("NIP"), max_length=20, blank=True, null=True)
    pesel = models.CharField(
        verbose_name=_("PESEL"), max_length=11, blank=True, null=True
    )
    address = models.CharField(verbose_name=_("Address"), max_length=100)
    zip_code = models.CharField(verbose_name=_("ZIP Code"), max_length=15)
    city = models.CharField(verbose_name=_("City"), max_length=60)
    country = models.ForeignKey(
        Country, verbose_name=_("Country"), on_delete=models.CASCADE, null=True
    )
    email = models.EmailField(verbose_name=_("Email"), blank=True, null=True)
    phone_number = models.CharField(
        verbose_name=_("Phone number"), max_length=20, blank=True, null=True
    )
    user = models.ForeignKey(
        User, verbose_name=_("User"), on_delete=models.CASCADE, null=True
    )

    class Meta:
        verbose_name_plural = _("persons")
        ordering = ["last_name"]
        unique_together = [
            "first_name",
            "last_name",
            "address",
            "zip_code",
            "city",
            "user",
        ]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name

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
