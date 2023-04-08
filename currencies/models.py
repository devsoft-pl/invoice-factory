from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext as _


class Currency(models.Model):
    code = models.CharField(verbose_name=_("Code"), max_length=10, unique=True)
    user = models.ForeignKey(
        User, verbose_name=_("User"), on_delete=models.CASCADE, null=True
    )

    def __str__(self):
        return self.code

    class Meta:
        verbose_name_plural = "currencies"
