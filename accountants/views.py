from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from accountants.forms import AccountantForm
from accountants.models import Accountant


@login_required
def list_accountants_view(request):
    accountants = Accountant.objects.filter(user=request.user)

    context = {"accountants": accountants, "current_module": "accountants"}
    return render(request, "accountants/list_accountants.html", context)


@login_required
def create_accountant_view(request):
    if request.method != "POST":
        form = AccountantForm(user=request.user)
    else:
        form = AccountantForm(data=request.POST, user=request.user)

        if form.is_valid():
            accountant = form.save(commit=False)
            accountant.user = request.user

            accountant.save()

            return redirect("accountants:list_accountants")

    context = {"form": form}
    return render(request, "accountants/create_accountant.html", context)


@login_required
def replace_accountant_view(request, accountant_id):
    accountant = get_object_or_404(Accountant, pk=accountant_id)

    if accountant.user != request.user:
        raise Http404(_("Accountant does not exist"))

    if request.method != "POST":
        form = AccountantForm(instance=accountant, user=request.user)
    else:
        form = AccountantForm(instance=accountant, data=request.POST, user=request.user)

        if form.is_valid():
            form.save()

            return redirect("accountants:list_accountants")

    context = {"form": form}
    return render(request, "accountants/replace_accountant.html", context)


@login_required
def delete_accountant_view(request, accountant_id):
    accountant = get_object_or_404(Accountant, pk=accountant_id)

    if accountant.user != request.user:
        raise Http404(_("Accountant does not exist"))

    accountant.delete()

    return redirect("accountants: list_accountants")
