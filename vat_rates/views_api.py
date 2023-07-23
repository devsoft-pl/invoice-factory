from rest_framework import viewsets

from base.mixins import OwnedObjectsMixin
from vat_rates.models import VatRate
from vat_rates.serializers import VatRateSerializer


class VatRateViewSet(OwnedObjectsMixin, viewsets.ModelViewSet):
    queryset = VatRate.objects.all()
    serializer_class = VatRateSerializer
