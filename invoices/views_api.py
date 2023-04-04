from django.contrib.auth.models import User
from django.http import HttpResponse
from django.template.loader import get_template
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from xhtml2pdf import pisa

from invoices.models import Company, Country, Currency, Invoice, Item, VatRate
from invoices.serializers import (CompanySerializer, CountrySerializer,
                                  CurrencySerializer, InvoiceSerializer,
                                  ItemSerializer, UserSerializer,
                                  VatRateSerializer)


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


def invoice_view(request):
    template_path = "invoice.html"
    context = {"myvar": "this is your template context"}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'filename="faktura.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(html, dest=response)
    # if error then show some funny view
    if pisa_status.err:
        return HttpResponse("We had some errors <pre>" + html + "</pre>")
    return response
