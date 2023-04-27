from django.urls import path

from currencies.views import (create_currency_view, delete_currency_view,
                              detail_currency_view, list_currencies_view,
                              replace_currency_view)

app_name = "currencies"
urlpatterns = [
    path("", list_currencies_view, name="list_currencies"),
    path("<int:currency_id>/", detail_currency_view, name="detail_currency"),
    path("create/", create_currency_view, name="create_currency"),
    path(
        "create_my_currency/",
        create_currency_view,
        name="create_my_currency",
        kwargs={"create_my_currency": True},
    ),
    path("replace/<int:currency_id>/", replace_currency_view, name="replace_currency"),
    path("delete/<int:currency_id>/", delete_currency_view, name="delete_currency"),
]
