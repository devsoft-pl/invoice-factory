from django.urls import path

from vat_rates.views import (create_vat_view, delete_vat_view, list_vates_view,
                             replace_vat_view)

app_name = "vat_rates"
urlpatterns = [
    path("", list_vates_view, name="list_vates"),
    path("create/", create_vat_view, name="create_vat"),
    path(
        "create_my_vat/",
        create_vat_view,
        name="create_my_vat",
        kwargs={"create_my_vat": True},
    ),
    path("replace/<int:vat_id>/", replace_vat_view, name="replace_vat"),
    path("delete/<int:vat_id>/", delete_vat_view, name="delete_vat"),
]
