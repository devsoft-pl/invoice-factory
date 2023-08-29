from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext as _

from companies.managers import MyClientsManager
from countries.models import Country


class Company(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=100)
    nip = models.CharField(
        verbose_name=_("NIP"),
        max_length=13,
        validators=[
            RegexValidator(
                r"^[0-9a-zA-Z]{8,16}$",
                _(
                    "Enter the tax ID without special characters with minimum 8 character"
                ),
            )
        ],
    )
    regon = models.CharField(
        verbose_name=_("Regon"),
        max_length=14,
        null=True,
        validators=[
            RegexValidator(
                r"^([0-9]{9}|[0-9]{14})$",
                _("Enter regon in numbers only with minimum 9 character"),
            )
        ],
    )
    country = models.ForeignKey(
        Country, verbose_name=_("Country"), on_delete=models.CASCADE, null=True
    )
    address = models.CharField(verbose_name=_("Address"), max_length=100)
    zip_code = models.CharField(
        verbose_name=_("ZIP Code"),
        max_length=10,
        validators=[
            RegexValidator(
                r"^[0-9]{2}-[0-9]{3}$", _("Zip code in numbers only in format xx-xxx")
            )
        ],
    )
    city = models.CharField(
        verbose_name=_("City"),
        max_length=60,
        validators=[
            RegexValidator(r"^[a-zA-Z ]+$", _("Enter the city in letters only"))
        ],
    )
    email = models.EmailField(verbose_name=_("Email"))
    phone_number = models.CharField(
        verbose_name=_("Phone number"),
        max_length=20,
        null=True,
        blank=True,
        validators=[
            RegexValidator(r"^[0-9]{9,}$", _("Enter phone number in numbers only"))
        ],
    )
    user = models.ForeignKey(
        User, verbose_name=_("User"), on_delete=models.CASCADE, null=True
    )
    is_my_company = models.BooleanField(
        verbose_name=_("Is my company"), default=False, editable=False
    )

    objects = models.Manager()
    my_clients = MyClientsManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = _("companies")
        ordering = ["name"]
        unique_together = ["nip", "regon", "user"]
