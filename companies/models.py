from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from base.validators import (
    foreign_nip_validator,
    foreign_zip_code_validator,
    polish_nip_validator,
    polish_zip_code_validator,
)
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

    def _validate_address_fields(self, nip_validator, zip_code_validator):
        errors = {}
        try:
            nip_validator(self.nip)
        except ValidationError as e:
            errors["nip"] = e
        try:
            zip_code_validator(self.zip_code)
        except ValidationError as e:
            errors["zip_code"] = e
        return errors

    def clean(self):
        super().clean()
        country_name = self.country.country.lower() if self.country else ""

        if country_name == "polska":
            errors = self._validate_address_fields(
                polish_nip_validator, polish_zip_code_validator
            )
        else:
            errors = self._validate_address_fields(
                foreign_nip_validator, foreign_zip_code_validator
            )

        if errors:
            raise ValidationError(errors)
