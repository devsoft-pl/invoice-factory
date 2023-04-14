from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render


def register_user_view(request):
    if request.method != "POST":
        form = UserCreationForm()
    else:
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            new_user = form.save()
            login(request, new_user)
            return redirect("invoices:index")

    context = {"form": form}
    return render(request, "registration/register.html", context)


@login_required
def detail_user_view(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    if user.id != request.user.id:
        raise Http404("User does not exist")

    context = {"user": user}
    return render(request, "registration/detail_user.html", context)


@login_required
def replace_user_view(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    if user.id != request.user.id:
        raise Http404("User does not exist")

    if request.method != "POST":
        form = UserChangeForm(instance=user)
    else:
        form = UserChangeForm(instance=user, data=request.POST)
        if form.is_valid():
            form.save()

            return redirect("users:detail_user")

    context = {"user": user, "form": form}
    return render(request, "registration/replace_user.html", context)
