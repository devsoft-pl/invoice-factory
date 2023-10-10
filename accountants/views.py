from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from accountants.models import Accountant


@login_required
def list_accountants_view(request):
    accountants = Accountant.objects.filter(user=request.user)

    context = {"accountants": accountants, "current_module": "accountants"}
    return render(request, "accountants/list_accountants.html", context)


@login_required
def create_accountant_view(request):
    pass


@login_required
def replace_accountant_view(request):
    pass


@login_required
def delete_accountant_view(request):
    pass
