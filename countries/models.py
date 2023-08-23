from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext as _


class Country(models.Model):
    country = models.CharField(
        verbose_name=_("Country"),
        max_length=30,
        validators=[
            RegexValidator(r"^[a-zA-Z ]{2,}$", _("Enter the country in letters only"))
        ],
    )
    user = models.ForeignKey(
        User, verbose_name=_("User"), on_delete=models.CASCADE, null=True
    )

    def __str__(self):
        return self.country

    class Meta:
        verbose_name_plural = _("countries")
        ordering = ["country"]
        unique_together = ["country", "user"]
