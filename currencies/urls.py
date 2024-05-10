from django.urls import path

from currencies.views import (
    create_currency_ajax_view,
    create_currency_view,
    delete_currency_view,
    list_currencies_view,
    replace_currency_view,
)

app_name = "currencies"
urlpatterns = [
    path("", list_currencies_view, name="list_currencies"),
    path("create/", create_currency_view, name="create_currency"),
    path("create_ajax/", create_currency_ajax_view, name="create_currency_ajax"),
    path("replace/<int:currency_id>/", replace_currency_view, name="replace_currency"),
    path("delete/<int:currency_id>/", delete_currency_view, name="delete_currency"),
]
