from django.urls import path

from invoices.views import invoice_view

app_name = "invoices"
urlpatterns = [path("invoice/", invoice_view, name="invoice_view")]
