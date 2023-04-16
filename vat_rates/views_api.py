from rest_framework import viewsets

from vat_rates.models import VatRate
from vat_rates.serializers import VatRateSerializer


class VatRateViewSet(viewsets.ModelViewSet):
    queryset = VatRate.objects.all()
    serializer_class = VatRateSerializer
