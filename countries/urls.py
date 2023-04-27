from django.urls import path

from countries.views import (create_country_view, delete_country_view,
                             detail_country_view, list_countries_view,
                             replace_country_view)

app_name = "countries"
urlpatterns = [
    path("", list_countries_view, name="list_countries"),
    path("<int:country_id>/", detail_country_view, name="detail_country"),
    path("create/", create_country_view, name="create_country"),
    path(
        "create_my_country/",
        create_country_view,
        name="create_my_country",
        kwargs={"create_my_ountry": True},
    ),
    path("replace/<int:country_id>/", replace_country_view, name="replace_country"),
    path("delete/<int:country_id>/", delete_country_view, name="delete_country"),
]
