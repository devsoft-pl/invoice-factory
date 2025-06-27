from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from companies.models import Company
from summary_recipients.models import SummaryRecipient


def get_user_company_or_404(company_id, user):
    company = get_object_or_404(Company.objects.select_related("user"), pk=company_id)
    if company.user != user:
        raise Http404(_("Company does not exist"))

    return company


def get_user_summary_recipient_or_404(summary_recipient_id, user):
    summary_recipient = get_object_or_404(
        SummaryRecipient.objects.select_related("company__user"),
        pk=summary_recipient_id,
    )
    if summary_recipient.company.user != user:
        raise Http404(_("Summary recipient does not exist"))

    return summary_recipient
