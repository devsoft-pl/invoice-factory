from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from companies.models import Company
from companies.serializers import CompanySerializer
from countries.models import Country
from countries.serializers import CountrySerializer
from currencies.models import Currency
from currencies.serializers import CurrencySerializer
from invoices.models import Invoice, Item, VatRate
from invoices.serializers import (InvoiceSerializer, ItemSerializer,
                                  UserSerializer)
from vat_rates.serializers import VatRateSerializer


class OwnedObjectsMixin:
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
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


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class CompanyViewSet(OwnedObjectsMixin, viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name", "nip", "regon"]


class InvoiceViewSet(OwnedObjectsMixin, viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    filter_backends = [
        filters.SearchFilter,
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ["invoice_number", "company__name"]
    filterset_fields = ["company__name", "invoice_type", "payment_date"]
    ordering_fields = ["invoice_number", "sale_date", "payment_date"]


class ItemViewSet(OwnedObjectsMixin, viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
