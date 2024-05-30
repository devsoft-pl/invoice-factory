from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from accountants.forms import AccountantForm
from accountants.models import Accountant
from companies.models import Company


@login_required
def list_accountants_view(request, company_id):
    company = get_object_or_404(Company, pk=company_id)
    accountants = Accountant.objects.filter(company=company)

    if company.user != request.user:
        raise Http404(_("Company does not exist"))

    context = {"company": company, "accountants": accountants}
    return render(request, "accountants/list_accountants.html", context)


@login_required
def create_accountant_view(request, company_id):
    company = get_object_or_404(Company, pk=company_id)

    if company.user != request.user:
        raise Http404(_("Company does not exist"))

    if request.method != "POST":
        form = AccountantForm()
    else:
        form = AccountantForm(data=request.POST)

        if form.is_valid():
            accountant = form.save(commit=False)
            accountant.company = company

            accountant.save()

            return redirect("accountants:list_accountants", company.pk)

    context = {"form": form, "company": company}
    return render(request, "accountants/create_accountant.html", context)


@login_required
def replace_accountant_view(request, accountant_id):
    accountant = get_object_or_404(Accountant, pk=accountant_id)

    if accountant.company.user != request.user:
        raise Http404(_("Accountant does not exist"))

    if request.method != "POST":
        form = AccountantForm(instance=accountant)
    else:
        form = AccountantForm(instance=accountant, data=request.POST)

        if form.is_valid():
            form.save()

            return redirect("accountants:list_accountants", accountant.company.pk)

    context = {
        "accountant": accountant,
        "form": form,
        "company": accountant.company,
    }
    return render(request, "accountants/replace_accountant.html", context)


@login_required
def delete_accountant_view(request, accountant_id):
    accountant = get_object_or_404(Accountant, pk=accountant_id)

    if accountant.company.user != request.user:
        raise Http404(_("Accountant does not exist"))

    accountant.delete()

    return redirect("accountants:list_accountants", accountant.company.pk)
