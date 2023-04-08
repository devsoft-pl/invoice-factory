from django.urls import path

from vat_rates.views import (
    list_vates_view,
    detail_vat_view,
    create_vat_view,
    replace_vat_view
)

app_name = "vat_rates"
urlpatterns = [
    path("", list_vates_view, name="list_vates"),
    path("<int:vat_id>/", detail_vat_view, name="detail_vat"),
    path("create/", create_vat_view, name="create_vat"),
    path("replace/<int:vat_id>/", replace_vat_view, name="replace_vat"),
]
