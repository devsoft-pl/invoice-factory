from rest_framework import viewsets

from countries.models import Country
from countries.serializers import CountrySerializer
from users.views_api import OwnedObjectsMixin


class CountryViewSet(OwnedObjectsMixin, viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
