from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from currencies.models import Currency

def get_user_currency_or_404(currency_id, user):
    currency = get_object_or_404(Currency.objects.select_related("user"), pk=currency_id)
    if currency.user != user:
        raise Http404(_("Currency does not exist"))
    return currency