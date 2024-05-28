from django.urls import path

from vat_rates.views import (
    create_vat_ajax_view,
    create_vat_view,
    delete_vat_view,
    list_vat_rates_view,
    replace_vat_view,
)

app_name = "vat_rates"
urlpatterns = [
    path("", list_vat_rates_view, name="list_vat_rates"),
    path("create/", create_vat_view, name="create_vat"),
    path("create_ajax/", create_vat_ajax_view, name="create_vat_ajax"),
    path("replace/<int:vat_id>/", replace_vat_view, name="replace_vat"),
    path("delete/<int:vat_id>/", delete_vat_view, name="delete_vat"),
]
