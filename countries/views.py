from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import redirect, render

from countries.forms import CountryForm
from countries.models import Country
from countries.utils import get_user_country_or_404


@login_required
def list_countries_view(request):
    countries_list = Country.objects.filter(user=request.user)

    total_countries = countries_list.count()

    paginator = Paginator(countries_list, 10)
    page = request.GET.get("page")
    try:
        countries = paginator.page(page)
    except PageNotAnInteger:
        countries = paginator.page(1)
    except EmptyPage:
        countries = paginator.page(paginator.num_pages)

    context = {
        "countries": countries,
        "total_countries": total_countries,
        "current_module": "countries",
    }
    return render(request, "countries/list_countries.html", context)


@login_required
def create_country_view(request):
    if request.method != "POST":
        form = CountryForm(current_user=request.user)
    else:
        form = CountryForm(data=request.POST, current_user=request.user)
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
        form = CountryForm(data=request.POST, current_user=request.user)
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
    country = get_user_country_or_404(country_id, request.user)

    if request.method != "POST":
        form = CountryForm(instance=country, current_user=request.user)
    else:
        form = CountryForm(
            instance=country, data=request.POST, current_user=request.user
        )
        if form.is_valid():
            form.save()
            return redirect("countries:list_countries")

    context = {"country": country, "form": form}
    return render(request, "countries/replace_country.html", context)


@login_required
def delete_country_view(request, country_id):
    country = get_user_country_or_404(country_id, request.user)
    country.delete()

    return redirect("countries:list_countries")
