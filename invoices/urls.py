from django.urls import path

from invoices.views import (create_currency_view, create_invoice_view,
                            delete_invoice_view, detail_invoice_view,
                            index_view, list_currencies_view,
                            list_invoices_view, pdf_invoice_view,
                            replace_invoice_view, update_invoice_view)

app_name = "invoices"
urlpatterns = [
    path("index/", index_view, name="index"),
    path("", list_invoices_view, name="list_invoices"),
    path("<int:invoice_id>/", detail_invoice_view, name="detail_invoice"),
    path("create/", create_invoice_view, name="create_invoice"),
    path("replace/<int:invoice_id>/", replace_invoice_view, name="replace_invoice"),
    path("update/<int:invoice_id>/", update_invoice_view, name="update_invoice"),
    path("delete/<int:invoice_id>/", delete_invoice_view, name="delete_invoice"),
    path("pdf/", pdf_invoice_view, name="pdf_invoice"),
    path("currencies/", list_currencies_view, name="list_currencies"),
    path("currencies/create/", create_currency_view, name="create_currency"),
]
