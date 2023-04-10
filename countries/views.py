from django.http import Http404
from django.shortcuts import redirect, render

from countries.forms import CountryForm
from countries.models import Country


def list_countries_view(request):
    countries = Country.objects.all()
    context = {"countries": countries}
    return render(request, "list_countries.html", context)


def detail_country_view(request, country_id):
    country = Country.objects.filter(pk=country_id).first()
    if not country:
        raise Http404("Invoice does not exist")
    context = {"country": country}
    return render(request, "detail_country.html", context)


def create_country_view(request):
    if request.method != "POST":
        initial = {"next": request.GET.get("next")}
        form = CountryForm(initial=initial)
    else:
        form = CountryForm(data=request.POST)
        if form.is_valid():
            form.save()

            next_url = form.cleaned_data["next"]
            if next_url:
                return redirect(next_url)

            return redirect("countries:list_countries")

    context = {"form": form}
    return render(request, "create_country.html", context)


def replace_country_view(request, country_id):
    country = Country.objects.filter(pk=country_id).first()
    if not country:
        raise Http404("Country does not exist")

    if request.method != "POST":
        form = CountryForm(instance=country)
    else:
        form = CountryForm(instance=country, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect("countries:list_countries")

    context = {"country": country, "form": form}
    return render(request, "replace_country.html", context)
