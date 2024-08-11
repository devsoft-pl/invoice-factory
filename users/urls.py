from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.urls import path, reverse_lazy

from users.forms import (
    LoginUserForm,
    PasswordResetConfirmUserForm,
    PasswordResetUserForm,
)
from users.views import (
    detail_user_view,
    password_change_user_view,
    register_user_view,
    replace_user_view,
)

app_name = "users"
urlpatterns = [
    path("login/", LoginView.as_view(form_class=LoginUserForm), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", register_user_view, name="register_user"),
    path(
        "password_change_user/", password_change_user_view, name="password_change_user"
    ),
    path(
        "password_reset_user/",
        PasswordResetView.as_view(
            success_url=reverse_lazy("users:password_reset_done"),
            form_class=PasswordResetUserForm,
        ),
        name="password_reset",
    ),
    path(
        "password_reset_user/done/",
        PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset_user/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            success_url=reverse_lazy("users:password_reset_complete"),
            form_class=PasswordResetConfirmUserForm,
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset_user/done/",
        PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path("me/", detail_user_view, name="detail_user"),
    path("replace/", replace_user_view, name="replace_user"),
]
