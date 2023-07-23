from rest_framework import viewsets

from base.mixins import OwnedObjectsMixin
from countries.models import Country
from countries.serializers import CountrySerializer


class CountryViewSet(OwnedObjectsMixin, viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
