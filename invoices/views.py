from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    viewsets,
    filters
)
from rest_framework import permissions
from rest_framework.authentication import TokenAuthentication

from invoices.serializers import (
    UserSerializer,
)

from invoices.models import (
    VatRate,
    Currency,
    Company,
    Invoice,
    Item,
)

from invoices.serializers import (
    VatRateSerializer,
    CurrencySerializer,
    CompanySerializer,
    InvoiceSerializer,
    ItemSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class VatRateViewSet(viewsets.ModelViewSet):
    queryset = VatRate.objects.all()
    serializer_class = VatRateSerializer


class CurrencyViewSet(viewsets.ModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'nip']


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['invoice_number', 'company__name']
    filterset_fields = ['company__name', 'invoice_type', 'payment_date']
    ordering_fields = ['invoice_number', 'sale_date', 'payment_date']


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer



