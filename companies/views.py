from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from companies.forms import CompanyFilterForm, CompanyForm
from companies.models import Company


@login_required
def list_companies_view(request):
    companies_list = Company.my_clients.filter(user=request.user)

    filter_form = CompanyFilterForm(request.GET)
    if filter_form.is_valid():
        name = filter_form.cleaned_data["name"]
        nip = filter_form.cleaned_data["nip"]
        regon = filter_form.cleaned_data["regon"]

        if name:
            companies_list = companies_list.filter(name__contains=name)
        if nip:
            companies_list = companies_list.filter(nip=nip)
        if regon:
            companies_list = companies_list.filter(regon=regon)

    paginator = Paginator(companies_list, 10)
    page = request.GET.get("page")
    try:
        companies = paginator.page(page)
    except PageNotAnInteger:
        companies = paginator.page(1)
    except EmptyPage:
        companies = paginator.page(paginator.num_pages)

    context = {"companies": companies, "filter_form": filter_form}
    return render(request, "companies/list_companies.html", context)


@login_required
def detail_company_view(request, company_id):
    company = get_object_or_404(Company, pk=company_id)

    if company.user != request.user:
        raise Http404(_("Company does not exist"))

    context = {"company": company}
    return render(request, "companies/detail_company.html", context)


@login_required
def create_company_view(request, create_my_company=False):
    if request.method != "POST":
        initial = {"next": request.GET.get("next")}
        form = CompanyForm(initial=initial, current_user=request.user)
    else:
        form = CompanyForm(data=request.POST, current_user=request.user)

        if form.is_valid():
            company = form.save(commit=False)
            company.user = request.user

            if create_my_company:
                company.is_my_company = True

            company.save()

            next_url = form.cleaned_data["next"]
            if next_url:
                return redirect(next_url)

            if create_my_company:
                return redirect("users:detail_user", request.user.pk)

            return redirect("companies:list_companies")

    context = {"form": form, "create_my_company": create_my_company}
    return render(request, "companies/create_company.html", context)


@login_required
def replace_company_view(request, company_id):
    company = get_object_or_404(Company, pk=company_id)

    if company.user != request.user:
        raise Http404(_("Company does not exist"))

    if request.method != "POST":
        form = CompanyForm(instance=company, current_user=request.user)
    else:
        form = CompanyForm(
            instance=company, data=request.POST, current_user=request.user
        )

        if form.is_valid():
            form.save()

            if company.is_my_company:
                return redirect("users:detail_user", request.user.pk)

            return redirect("companies:list_companies")

    context = {"company": company, "form": form}
    return render(request, "companies/replace_company.html", context)


@login_required
def delete_company_view(request, company_id):
    company = get_object_or_404(Company, pk=company_id)

    if company.user != request.user:
        raise Http404(_("Company does not exist"))

    company.delete()

    if company.is_my_company:
        return redirect("users:detail_user", request.user.pk)

    return redirect("companies:list_companies")
