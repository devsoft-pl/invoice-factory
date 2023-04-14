from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import (
    redirect,
    render,
    get_object_or_404
)


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


def detail_user_view(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    context = {"user": user}
    return render(request, "registration/detail_user.html", context)
