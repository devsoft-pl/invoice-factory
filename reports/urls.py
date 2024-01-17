from django.urls import path

from reports.views import list_reports_view

app_name = "reports"
urlpatterns = [
    path("", list_reports_view, name="list_reports"),
]
