from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from base.mixins import OwnedObjectsMixin
from companies.models import Company
from companies.serializers import CompanySerializer


class CompanyViewSet(OwnedObjectsMixin, viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name", "nip", "regon"]
