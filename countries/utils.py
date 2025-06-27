from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from countries.models import Country


def get_user_country_or_404(country_id, user):
    country = get_object_or_404(Country.objects.select_related("user"), pk=country_id)
    if country.user != user:
        raise Http404(_("Country does not exist"))

    return country
