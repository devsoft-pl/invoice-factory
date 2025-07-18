from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from accountants.forms import AccountantForm
from accountants.models import Accountant
from accountants.utils import get_user_accountant_or_404, get_user_company_or_404


@login_required
def list_accountants_view(request, company_id):
    company = get_user_company_or_404(company_id, request.user)
    accountants = Accountant.objects.filter(company=company).select_related("company")

    context = {"company": company, "accountants": accountants}
    return render(request, "accountants/list_accountants.html", context)


@login_required
def create_accountant_view(request, company_id):
    company = get_user_company_or_404(company_id, request.user)

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
    accountant = get_user_accountant_or_404(accountant_id, request.user)

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
    accountant = get_user_accountant_or_404(accountant_id, request.user)
    accountant.delete()

    return redirect("accountants:list_accountants", accountant.company.pk)
