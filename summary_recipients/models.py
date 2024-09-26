from django.conf import settings
from django.core.mail import EmailMessage
from django.db import models
from django.utils.translation import gettext_lazy as _

from companies.models import Company


class SummaryRecipient(models.Model):
    MONTHLY = 0
    QUARTERLY = 1

    SETTLEMENT_TYPES = (
        (MONTHLY, _("Monthly")),
        (QUARTERLY, _("Quarterly")),
    )

    description = models.CharField(verbose_name=_("Description"), max_length=50)
    company = models.ForeignKey(
        Company,
        verbose_name=_("Company"),
        on_delete=models.CASCADE,
        related_name="summary_recipients",
    )
    day = models.IntegerField(verbose_name=_("Day of send"))
    email = models.EmailField(_("Email"))
    settlement_types = models.IntegerField(
        verbose_name=_("Settlement types"), choices=SETTLEMENT_TYPES
    )
    final_call = models.BooleanField(verbose_name=_("Final call"), default=False)
    is_last_day = models.BooleanField(
        verbose_name=_("Last day in month"), default=False
    )

    def __str__(self):
        return self.description

    def send_email(self, subject, content, files=None):
        email = EmailMessage(
            subject,
            content,
            settings.EMAIL_SENDER,
            [self.email],
        )

        if files:
            for data in files:
                email.attach(data["name"], data["content"])

        return email.send()
