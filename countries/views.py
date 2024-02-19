from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from countries.forms import CountryForm
from countries.models import Country


@login_required
def list_countries_view(request):
    countries_list = Country.objects.filter(user=request.user)

    paginator = Paginator(countries_list, 10)
    page = request.GET.get("page")
    try:
        countries = paginator.page(page)
    except PageNotAnInteger:
        countries = paginator.page(1)
    except EmptyPage:
        countries = paginator.page(paginator.num_pages)

    context = {"countries": countries, "current_module": "countries"}
    return render(request, "countries/list_countries.html", context)


@login_required
def create_country_view(request):
    if request.method != "POST":
        form = CountryForm(user=request.user)
    else:
        form = CountryForm(data=request.POST, user=request.user)

        if form.is_valid():
            country = form.save(commit=False)
            country.user = request.user

            country.save()

            return redirect("countries:list_countries")

    context = {"form": form}
    return render(request, "countries/create_country.html", context)


@login_required
def create_country_ajax_view(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(permitted_methods=["POST"])
    else:
        form = CountryForm(data=request.POST, user=request.user)

        if form.is_valid():
            country = form.save(commit=False)
            country.user = request.user

            country.save()

            return JsonResponse(
                {
                    "success": True,
                    "id": country.id,
                    "name": country.country.capitalize(),
                }
            )

        else:
            return JsonResponse({"success": False, "errors": form.errors})


@login_required
def replace_country_view(request, country_id):
    country = get_object_or_404(Country, pk=country_id)

    if country.user != request.user:
        raise Http404(_("Country does not exist"))

    if request.method != "POST":
        form = CountryForm(instance=country, user=request.user)
    else:
        form = CountryForm(instance=country, data=request.POST, user=request.user)

        if form.is_valid():
            form.save()

            return redirect("countries:list_countries")

    context = {"country": country, "form": form}
    return render(request, "countries/replace_country.html", context)


@login_required
def delete_country_view(request, country_id):
    country = get_object_or_404(Country, pk=country_id)

    if country.user != request.user:
        raise Http404(_("Country does not exist"))

    country.delete()

    return redirect("countries:list_countries")
