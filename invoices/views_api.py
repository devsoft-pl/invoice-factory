from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from base.mixins import OwnedObjectsMixin
from invoices.models import Invoice
from invoices.serializers import InvoiceSerializer


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
