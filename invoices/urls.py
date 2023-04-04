from django.urls import path

from invoices.views import index_view, invoice_view

app_name = "invoices"
urlpatterns = [
    path("invoice/index", index_view, name="index"),
    path("invoice/", invoice_view, name="invoice_view"),
]
