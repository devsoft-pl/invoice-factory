from django.urls import path

from companies.views import (create_company_view,
                             create_summary_recipient_view,
                             delete_company_view,
                             delete_summary_recipient_view,
                             detail_company_view, list_companies_view,
                             list_summary_recipients_view,
                             replace_company_view,
                             replace_summary_recipient_view, settings_company_view)

app_name = "companies"
urlpatterns = [
    path("", list_companies_view, name="list_companies"),
    path(
        "my_companies/",
        list_companies_view,
        name="list_my_companies",
        kwargs={"my_companies": True},
    ),
    path("<int:company_id>/", detail_company_view, name="detail_company"),
    path("create/", create_company_view, name="create_company"),
    path(
        "create_my_company/",
        create_company_view,
        name="create_my_company",
        kwargs={"create_my_company": True},
    ),
    path("replace/<int:company_id>/", replace_company_view, name="replace_company"),
    path("delete/<int:company_id>/", delete_company_view, name="delete_company"),
    path(
        "<int:company_id>/settings_company/",
        settings_company_view,
        name="settings_company",
    ),
    path(
        "<int:company_id>/settings_company/summary_recipients/",
        list_summary_recipients_view,
        name="list_summary_recipients",
    ),
    path(
        "<int:company_id>/settings_company/summary_recipient/create/",
        create_summary_recipient_view,
        name="create_summary_recipient",
    ),
    path(
        "settings_company/summary_recipient/delete/<int:summary_recipient_id>/",
        delete_summary_recipient_view,
        name="delete_summary_recipient",
    ),
    path(
        "settings_company/summary_recipient/replace/<int:summary_recipient_id>/",
        replace_summary_recipient_view,
        name="replace_summary_recipient",
    ),
]
