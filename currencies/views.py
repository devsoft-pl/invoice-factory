from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from currencies.forms import CurrencyForm
from currencies.models import Currency


@login_required
def list_currencies_view(request):
    currencies_list = Currency.objects.filter(user=request.user)

    paginator = Paginator(currencies_list, 10)
    page = request.GET.get("page")
    try:
        currencies = paginator.page(page)
    except PageNotAnInteger:
        currencies = paginator.page(1)
    except EmptyPage:
        currencies = paginator.page(paginator.num_pages)

    context = {"currencies": currencies, "current_module": "currencies"}
    return render(request, "currencies/list_currencies.html", context)


@login_required
def create_currency_view(request):
    if request.method != "POST":
        form = CurrencyForm(user=request.user)
    else:
        form = CurrencyForm(data=request.POST, user=request.user)

        if form.is_valid():
            currency = form.save(commit=False)
            currency.user = request.user

            currency.save()

            return redirect("currencies:list_currencies")

    context = {"form": form}
    return render(request, "currencies/create_currency.html", context)


@login_required
def create_currency_ajax_view(request):
    if request.method != "POST":
        form = CurrencyForm(user=request.user)
    else:
        form = CurrencyForm(data=request.POST, user=request.user)

        if form.is_valid():
            currency = form.save(commit=False)
            currency.user = request.user

            currency.save()

            return JsonResponse(
                {"success": True, "id": currency.id, "name": currency.code.upper()}
            )

        else:
            return JsonResponse({"success": False, "errors": form.errors})

    context = {"form": form}
    return render(request, "currencies/create_currency_ajax.html", context)


@login_required
def replace_currency_view(request, currency_id):
    currency = get_object_or_404(Currency, pk=currency_id)

    if currency.user != request.user:
        raise Http404(_("Currency does not exist"))

    if request.method != "POST":
        form = CurrencyForm(instance=currency, user=request.user)
    else:
        form = CurrencyForm(instance=currency, data=request.POST, user=request.user)

        if form.is_valid():
            form.save()

            return redirect("currencies:list_currencies")

    context = {"currency": currency, "form": form}
    return render(request, "currencies/replace_currency.html", context)


@login_required
def delete_currency_view(request, currency_id):
    currency = get_object_or_404(Currency, pk=currency_id)

    if currency.user != request.user:
        raise Http404(_("Currency does not exist"))

    currency.delete()

    return redirect("currencies:list_currencies")
