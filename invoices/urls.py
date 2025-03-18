from django.urls import path

from invoices.views import (
    create_buy_invoice_view,
    create_sell_invoice_view,
    create_sell_person_invoice_view,
    create_sell_person_to_client_invoice_view,
    delete_invoice_view,
    detail_invoice_view,
    duplicate_invoice_view,
    list_invoices_view,
    pdf_invoice_view,
    replace_buy_invoice_view,
    replace_sell_invoice_view,
    replace_sell_person_to_client_invoice_view,
)

app_name = "invoices"
urlpatterns = [
    path("", list_invoices_view, name="list_invoices"),
    path("<int:invoice_id>/", detail_invoice_view, name="detail_invoice"),
    path("create_sell_invoice/", create_sell_invoice_view, name="create_sell_invoice"),
    path("create_buy_invoice/", create_buy_invoice_view, name="create_buy_invoice"),
    path(
        "create_sell_person_invoice/",
        create_sell_person_invoice_view,
        name="create_sell_person_invoice",
    ),
    path(
        "create_sell_person_to_client_invoice/",
        create_sell_person_to_client_invoice_view,
        name="create_sell_person_to_client_invoice",
    ),
    path(
        "duplicate_invoice/<int:invoice_id>/",
        duplicate_invoice_view,
        name="duplicate_invoice",
    ),
    path(
        "replace_sell_invoice/<int:invoice_id>/",
        replace_sell_invoice_view,
        name="replace_sell_invoice",
    ),
    path(
        "replace_sell_person_to_client_invoice/<int:invoice_id>/",
        replace_sell_person_to_client_invoice_view,
        name="replace_sell_person_to_client_invoice",
    ),
    path(
        "create_correction_invoice/<int:invoice_id>/",
        replace_sell_invoice_view,
        name="create_correction_invoice",
        kwargs={"create_correction": True},
    ),
    path(
        "create_correction_person_to_client_invoice/<int:invoice_id>/",
        replace_sell_person_to_client_invoice_view,
        name="create_correction_person_to_client_invoice",
        kwargs={"create_correction": True},
    ),
    path(
        "replace_buy_invoice/<int:invoice_id>/",
        replace_buy_invoice_view,
        name="replace_buy_invoice",
    ),
    path("delete/<int:invoice_id>/", delete_invoice_view, name="delete_invoice"),
    path("pdf/<int:invoice_id>/", pdf_invoice_view, name="pdf_invoice"),
]
