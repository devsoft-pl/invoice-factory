from django.urls import path

from accountants.views import (create_accountant_view, delete_accountant_view,
                               list_accountants_view, replace_accountant_view)

app_name = "accountants"
urlpatterns = [
    path("", list_accountants_view, name="list_accountants"),
    path("create/", create_accountant_view, name="create_accountant"),
    path("replace/", replace_accountant_view, name="replace_accountant"),
    path("delete/", delete_accountant_view, name="delete_accountant"),
]
