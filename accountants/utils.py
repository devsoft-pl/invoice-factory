from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from accountants.models import Accountant
from companies.models import Company


def get_user_company_or_404(company_id, user):
    company = get_object_or_404(Company.objects.select_related("user"), pk=company_id)
    if company.user != user:
        raise Http404(_("Company does not exist"))

    return company


def get_user_accountant_or_404(accountant_id, user):
    accountant = get_object_or_404(
        Accountant.objects.select_related("company__user"), pk=accountant_id
    )
    if accountant.company.user != user:
        raise Http404(_("Accountant does not exist"))

    return accountant
