from django.urls import path

from invoices.views import (create_invoice_view, delete_invoice_view,
                            detail_invoice_view, index_view,
                            list_invoices_view, pdf_invoice_view,
                            replace_invoice_view, update_invoice_view)

app_name = "invoices"
urlpatterns = [
    path("index/", index_view, name="index"),
    path("", list_invoices_view, name="list"),
    path("<int:invoice_id>/", detail_invoice_view, name="detail"),
    path("create/", create_invoice_view, name="create"),
    path("replace/<int:invoice_id>/", replace_invoice_view, name="replace"),
    path("update/<int:invoice_id>/", update_invoice_view, name="update"),
    path("delete/<int:invoice_id>/", delete_invoice_view, name="delete"),
    path("pdf/", pdf_invoice_view, name="pdf"),
    # path("invoice/", invoice_view, name="invoice_view")
]
