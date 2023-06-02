from django.urls import path

from countries.views import (create_country_view, delete_country_view,
                             list_countries_view, replace_country_view)

app_name = "countries"
urlpatterns = [
    path("", list_countries_view, name="list_countries"),
    path("create/", create_country_view, name="create_country"),
    path("replace/<int:country_id>/", replace_country_view, name="replace_country"),
    path("delete/<int:country_id>/", delete_country_view, name="delete_country"),
]
