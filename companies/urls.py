from django.urls import path

from companies.views import (create_company_view, delete_company_view,
                             detail_company_view, list_companies_view,
                             replace_company_view)

app_name = "companies"
urlpatterns = [
    path("", list_companies_view, name="list_companies"),
    path("<int:company_id>/", detail_company_view, name="detail_company"),
    path("create/", create_company_view, name="create_company"),
    path("replace/<int:company_id>/", replace_company_view, name="replace_company"),
    path("delete/<int:company_id>/", delete_company_view, name="delete_company"),
]
