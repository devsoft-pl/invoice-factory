from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from vat_rates.models import VatRate


def get_user_vat_rate_or_404(vat_id, user):
    vat_rate = get_object_or_404(VatRate.objects.select_related("user"), pk=vat_id)
    if vat_rate.user != user:
        raise Http404(_("Vat rate does not exist"))
    return vat_rate
