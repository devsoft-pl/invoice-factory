from rest_framework import viewsets

from currencies.models import Currency
from currencies.serializers import CurrencySerializer
from users.views_api import OwnedObjectsMixin


class CurrencyViewSet(OwnedObjectsMixin, viewsets.ModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
