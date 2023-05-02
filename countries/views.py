from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from countries.forms import CountryForm
from countries.models import Country


@login_required
def list_countries_view(request):
    countries = Country.objects.filter(user=request.user)

    context = {"countries": countries}
    return render(request, "countries/list_countries.html", context)


@login_required
def detail_country_view(request, country_id):
    country = get_object_or_404(Country, pk=country_id)

    if country.user != request.user:
        raise Http404(_("Country does not exist"))

    context = {"country": country}
    return render(request, "countries/detail_country.html", context)


@login_required
def create_country_view(request, create_my_country=False):
    if request.method != "POST":
        initial = {"next": request.GET.get("next")}
        form = CountryForm(initial=initial)
    else:
        form = CountryForm(data=request.POST)

        if form.is_valid():
            country = form.save(commit=False)
            country.user = request.user

            if create_my_country:
                country.is_my_country = True

            country.save()

            next_url = form.cleaned_data["next"]
            if next_url:
                return redirect(next_url)

            if create_my_country:
                return redirect("users:detail_user", request.user.pk)

            return redirect("countries:list_countries")

    context = {"form": form, "create_my_country": create_my_country}
    return render(request, "countries/create_country.html", context)


@login_required
def replace_country_view(request, country_id):
    country = get_object_or_404(Country, pk=country_id)

    if country.user != request.user:
        raise Http404(_("Country does not exist"))

    if request.method != "POST":
        form = CountryForm(instance=country)
    else:
        form = CountryForm(instance=country, data=request.POST)

        if form.is_valid():
            form.save()

            if country.is_my_country:
                return redirect("users:detail_user", request.user.pk)

            return redirect("countries:list_countries")

    context = {"country": country, "form": form}
    return render(request, "countries/replace_country.html", context)


@login_required
def delete_country_view(request, country_id):
    country = get_object_or_404(Country, pk=country_id)

    if country.user != request.user:
        raise Http404(_("Country does not exist"))

    country.delete()

    if country.is_my_country:
        return redirect("users:detail_user", request.user.pk)

    return redirect("countries:list_countries")
