from django.http import Http404
from django.shortcuts import redirect, render

from companies.forms import CompanyForm
from companies.models import Company


def list_companies_view(request):
    companies = Company.objects.all()
    context = {"companies": companies}
    return render(request, "list_companies.html", context)


def detail_company_view(request, company_id):
    company = Company.objects.filter(pk=company_id).first()
    if not company:
        raise Http404("Invoice does not exist")
    context = {"company": company}
    return render(request, "detail_company.html", context)


def create_company_view(request):
    if request.method != "POST":
        initial = {"next": request.GET.get("next")}
        form = CompanyForm(initial=initial)
    else:
        form = CompanyForm(data=request.POST)
        if form.is_valid():
            form.save()

            next_url = form.cleaned_data["next"]
            if next_url:
                return redirect(next_url)

            return redirect("companies:list_companies")

    context = {"form": form}
    return render(request, "create_company.html", context)
