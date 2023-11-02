from django.urls import path

from summary_recipients.views import (create_summary_recipient_view,
                                      delete_summary_recipient_view,
                                      list_summary_recipients_view,
                                      replace_summary_recipient_view)

app_name = "summary_recipients"
urlpatterns = [
    path(
        "<int:company_id>/summary_recipients/",
        list_summary_recipients_view,
        name="list_summary_recipients",
    ),
    path(
        "<int:company_id>/summary_recipient/create/",
        create_summary_recipient_view,
        name="create_summary_recipient",
    ),
    path(
        "summary_recipient/delete/<int:summary_recipient_id>/",
        delete_summary_recipient_view,
        name="delete_summary_recipient",
    ),
    path(
        "summary_recipient/replace/<int:summary_recipient_id>/",
        replace_summary_recipient_view,
        name="replace_summary_recipient",
    ),
]
