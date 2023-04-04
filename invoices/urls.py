from django.urls import path

from invoices.views import (create_invoice_view, delete_invoice_view,
                            detail_invoice_view, invoice_pdf_view,
                            invoices_view, replace_invoice_view,
                            update_invoice_view)

app_name = "invoices"
urlpatterns = [
    path("invoices/", invoices_view, name="invoices"),
    path("invoices/<int:invoice_id>/", detail_invoice_view, name="detail"),
    path("invoices/create/", create_invoice_view, name="create"),
    path("invoices/<int:invoice_id>/", replace_invoice_view, name="replace"),
    path("invoices/<int:invoice_id>/", update_invoice_view, name="update"),
    path("invoices/<int:invoice_id>/", delete_invoice_view, name="delete"),
    path("invoices/pdf/", invoice_pdf_view, name="pdf"),
    # path("invoice/", invoice_view, name="invoice_view")
]
