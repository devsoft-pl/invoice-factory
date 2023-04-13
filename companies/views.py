from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from companies.forms import CompanyForm
from companies.models import Company


@login_required
def list_companies_view(request):
    companies = Company.objects.filter(user=request.user)

    context = {"companies": companies}
    return render(request, "companies/list_companies.html", context)


@login_required
def detail_company_view(request, company_id):
    company = get_object_or_404(Company, pk=company_id)

    if company.user != request.user:
        raise Http404("Company does not exist")

    context = {"company": company}
    return render(request, "companies/detail_company.html", context)


@login_required
def create_company_view(request):
    if request.method != "POST":
        initial = {"next": request.GET.get("next")}
        form = CompanyForm(initial=initial)
    else:
        form = CompanyForm(data=request.POST)
        if form.is_valid():
            company = form.save(commit=False)
            company.user = request.user
            company.save()

            next_url = form.cleaned_data["next"]
            if next_url:
                return redirect(next_url)

            return redirect("companies:list_companies")

    context = {"form": form}
    return render(request, "companies/create_company.html", context)


@login_required
def replace_company_view(request, company_id):
    company = get_object_or_404(Company, pk=company_id)

    if company.user != request.user:
        raise Http404("Company does not exist")

    if request.method != "POST":
        form = CompanyForm(instance=company)
    else:
        form = CompanyForm(instance=company, data=request.POST)
        if form.is_valid():
            form.save()

            return redirect("companies:list_companies")

    context = {"company": company, "form": form}
    return render(request, "companies/replace_company.html", context)


@login_required
def delete_company_view(request, company_id):
    company = get_object_or_404(Company, pk=company_id)

    if company.user != request.user:
        raise Http404("Company does not exist")

    company.delete()
    return redirect("companies:list_companies")
