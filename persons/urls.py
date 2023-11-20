from django.urls import path

from persons.views import list_persons_view

app_name = "persons"
urlpatterns = [
    path("", list_persons_view, name="list_persons"),
]
