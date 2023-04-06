from django.urls import path

from countries.views import (create_country_view, detail_country_view,
                             list_countries_view)

app_name = "countries"
urlpatterns = [
    path("", list_countries_view, name="list_countries"),
    path("<int:country_id>/", detail_country_view, name="detail_country"),
    path("create/", create_country_view, name="create_country"),
]
