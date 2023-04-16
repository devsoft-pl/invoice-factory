from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import (
    UserCreationForm,
)
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from companies.models import Company
from users.forms import UserForm


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

    my_companies = Company.objects.filter(user=request.user, is_my_company=True)

    context = {"user": user, "my_companies": my_companies}
    return render(request, "registration/detail_user.html", context)


@login_required
def replace_user_view(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    if user.id != request.user.id:
        raise Http404("User does not exist")

    if request.method != "POST":
        form = UserForm(instance=user)
    else:
        form = UserForm(instance=user, data=request.POST)
        if form.is_valid():
            form.save()

            return redirect("users:detail_user", request.user.pk)

    context = {"user": user, "form": form}
    return render(request, "registration/replace_user.html", context)
