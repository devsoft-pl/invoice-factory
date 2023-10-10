from django.urls import path

from accountants.views import (create_accountant_view, delete_accountant_view,
                               detail_accountant_view, replace_accountant_view)

app_name = "accountants"
urlpatterns = [
    path("accountant/", detail_accountant_view, name="detail_accountant"),
    path("create/", create_accountant_view, name="create_accountant"),
    path("replace/", replace_accountant_view, name="replace_accountant"),
    path("delete/", delete_accountant_view, name="delete_accountant"),
]
