from django.urls import path

from companies.views import (create_company_view, detail_company_view,
                             list_companies_view)

app_name = "companies"
urlpatterns = [
    path("", list_companies_view, name="list_companies"),
    path("<int:company_id>/", detail_company_view, name="detail_company"),
    path("create/", create_company_view, name="create_company"),
]
