from django.urls import path

from persons.views import (
    create_person_ajax_view,
    create_person_view,
    delete_person_view,
    detail_person_view,
    list_persons_view,
    replace_person_view,
)

app_name = "persons"
urlpatterns = [
    path("", list_persons_view, name="list_persons"),
    path("detail/<int:person_id>", detail_person_view, name="detail_person"),
    path("create/", create_person_view, name="create_person"),
    path("create_ajax/", create_person_ajax_view, name="create_person_ajax"),
    path("replace/<int:person_id>/", replace_person_view, name="replace_person"),
    path("delete/<int:person_id>/", delete_person_view, name="delete_person"),
]
