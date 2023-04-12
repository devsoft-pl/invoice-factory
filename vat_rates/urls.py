from django.urls import path

from vat_rates.views import (create_vat_view, delete_vat_view, detail_vat_view,
                             list_vates_view, replace_vat_view)

app_name = "vat_rates"
urlpatterns = [
    path("", list_vates_view, name="list_vates"),
    path("<int:vat_id>/", detail_vat_view, name="detail_vat"),
    path("create/", create_vat_view, name="create_vat"),
    path("replace/<int:vat_id>/", replace_vat_view, name="replace_vat"),
    path("delete/<int:vat_id>/", delete_vat_view, name="delete_vat"),
]
