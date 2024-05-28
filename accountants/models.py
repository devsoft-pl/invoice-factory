from django.db import models
from django.utils.translation import gettext as _

from companies.models import Company


class Accountant(models.Model):
    name = models.CharField(_("Name"), max_length=100, default=None)
    email = models.EmailField(_("Email"))
    phone_number = models.CharField(
        verbose_name=_("Phone number"), max_length=20, null=True, blank=True
    )
    company = models.ForeignKey(
        Company,
        verbose_name=_("Company"),
        on_delete=models.CASCADE,
        related_name="summary_recipient",
    )

    class Meta:
        verbose_name_plural = _("accountants")
        unique_together = ["email", "company"]

    def __str__(self):
        return self.name
