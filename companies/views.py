from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from companies.forms import CompanyFilterForm, CompanyForm
from companies.models import Company
from companies.utils import get_user_company_or_404


@login_required
def list_companies_view(request, my_companies=False):
    if my_companies:
        companies_list = Company.objects.filter(user=request.user, is_my_company=True)
    else:
        companies_list = Company.my_clients.filter(user=request.user)

    filter_form = CompanyFilterForm(request.GET)
    if filter_form.is_valid():
        companies_list = filter_form.get_filtered_companies(companies_list)

    total_companies = companies_list.count()

    paginator = Paginator(companies_list, 10)
    page = request.GET.get("page")
    try:
        companies = paginator.page(page)
    except PageNotAnInteger:
        companies = paginator.page(1)
    except EmptyPage:
        companies = paginator.page(paginator.num_pages)

    context = {
        "companies": companies,
        "total_companies": total_companies,
        "filter_form": filter_form,
    }

    if my_companies:
        context.update({"current_module": "my_companies"})
        template_name = "companies/list_my_companies.html"
    else:
        context.update({"current_module": "companies"})
        template_name = "companies/list_companies.html"

    return render(request, template_name, context)


@login_required
def detail_company_view(request, company_id):
    queryset = Company.objects.select_related("user", "country")
    company = get_object_or_404(queryset, pk=company_id)

    if company.user != request.user:
        raise Http404(_("Company does not exist"))

    context = {"company": company}
    return render(request, "companies/detail_company.html", context)


@login_required
def create_company_view(request, create_my_company=False):
    if request.method != "POST":
        form = CompanyForm(current_user=request.user)
    else:
        form = CompanyForm(data=request.POST, current_user=request.user)
        if form.is_valid():
            company = form.save(commit=False)
            company.user = request.user
            if create_my_company:
                company.is_my_company = True

            company.save()

            if create_my_company:
                return redirect("companies:list_my_companies")

            return redirect("companies:list_companies")

    context = {"form": form, "create_my_company": create_my_company}
    return render(request, "companies/create_company.html", context)


@login_required
def create_company_ajax_view(request, create_my_company=False):
    if request.method != "POST":
        form = CompanyForm(current_user=request.user)
    else:
        form = CompanyForm(data=request.POST, current_user=request.user)
        if form.is_valid():
            company = form.save(commit=False)
            company.user = request.user

            if create_my_company:
                company.is_my_company = True

            company.save()

            return JsonResponse(
                {
                    "success": True,
                    "id": company.id,
                    "name": company.name,
                }
            )
        else:
            return JsonResponse({"success": False, "errors": form.errors})

    context = {"form": form, "create_my_company": create_my_company}
    return render(request, "companies/create_company_ajax.html", context)


@login_required
def replace_company_view(request, company_id):
    company = get_user_company_or_404(company_id, request.user)

    if request.method != "POST":
        form = CompanyForm(instance=company, current_user=request.user)
    else:
        form = CompanyForm(
            instance=company, data=request.POST, current_user=request.user
        )
        if form.is_valid():
            form.save()

            if company.is_my_company:
                return redirect("companies:list_my_companies")

            return redirect("companies:list_companies")

    context = {"company": company, "form": form}
    return render(request, "companies/replace_company.html", context)


@login_required
def delete_company_view(request, company_id):
    company = get_user_company_or_404(company_id, request.user)
    company.delete()

    if company.is_my_company:
        return redirect("companies:list_my_companies")

    return redirect("companies:list_companies")


@login_required
def settings_company_view(request, company_id):
    company = get_user_company_or_404(company_id, request.user)

    context = {"company": company}
    return render(request, "companies/settings_company.html", context)
