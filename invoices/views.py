from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework import permissions
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


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer



