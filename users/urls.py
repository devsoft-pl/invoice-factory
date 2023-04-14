from django.urls import include, path

from users.views import (
    register_user_view,
    detail_user_view
)

app_name = "users"
urlpatterns = [
    path("", include("django.contrib.auth.urls")),
    path("register/", register_user_view, name="register_user"),
    path("<int:user_id>/", detail_user_view, name="detail_user"),
]
