from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from users.forms import PasswordChangeUserForm, UserCreationForm, UserForm


def register_user_view(request):
    if request.method != "POST":
        form = UserCreationForm()
    else:
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            new_user = form.save()
            login(request, new_user)
            return redirect("index")

    context = {"form": form}
    return render(request, "registration/register.html", context)


def password_change_user_view(request):
    if not request.user.is_authenticated:
        raise Http404(_("User does not authenticated"))

    if request.method != "POST":
        form = PasswordChangeUserForm(user=request.user)
    else:
        form = PasswordChangeUserForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)

            return redirect("users:detail_user")

    context = {"user": request.user, "form": form}
    return render(request, "registration/password_change_user.html", context)


@login_required
def detail_user_view(request):
    context = {"user": request.user, "current_module": "users"}
    return render(request, "registration/detail_user.html", context)


@login_required
def replace_user_view(request):
    user = request.user

    if request.method != "POST":
        form = UserForm(instance=user)
    else:
        form = UserForm(instance=user, data=request.POST)
        if form.is_valid():
            form.save()

            return redirect("users:detail_user")

    context = {"user": user, "form": form}
    return render(request, "registration/replace_user.html", context)
