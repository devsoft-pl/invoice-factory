from rest_framework import viewsets

from base.mixins import OwnedObjectsMixin
from currencies.models import Currency
from currencies.serializers import CurrencySerializer


class CurrencyViewSet(OwnedObjectsMixin, viewsets.ModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
