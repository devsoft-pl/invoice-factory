from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    viewsets,
    filters
)

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


class OwnedObjectsMixin:  # mxin domieszka, dodanie funkcjonalności do istniejącej klasy
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return super().get_queryset()
        else:
            return super().get_queryset().filter(user_id=user.id)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return super().get_queryset()
        else:
            return super().get_queryset().filter(id=user.id)


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



