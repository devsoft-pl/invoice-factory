from django.http import Http404
from django.shortcuts import redirect, render

from currencies.forms import CurrencyForm
from currencies.models import Currency


def list_currencies_view(request):
    currencies = Currency.objects.all()
    context = {"currencies": currencies}
    return render(request, "list_currencies.html", context)


def detail_currency_view(request, currency_id):
    currency = Currency.objects.filter(pk=currency_id).first()
    if not currency:
        raise Http404("Currency does not exist")

    context = {"currency": currency}
    return render(request, "detail_currency.html", context)


def create_currency_view(request):
    if request.method != "POST":
        initial = {"next": request.GET.get("next")}
        form = CurrencyForm(initial=initial)
    else:
        form = CurrencyForm(data=request.POST)
        if form.is_valid():
            form.save()

            next_url = form.cleaned_data["next"]
            if next_url:
                return redirect(next_url)

            return redirect("currencies:list_currencies")

    context = {"form": form}
    return render(request, "create_currency.html", context)


def replace_currency_view(request, currency_id):
    currency = Currency.objects.filter(pk=currency_id).first()
    if not currency:
        raise Http404("Currency does not exist")

    if request.method != "POST":
        form = CurrencyForm(instance=currency)
    else:
        form = CurrencyForm(instance=currency, data=request.POST)
        if form.is_valid():
            form.save()

            return redirect("invoices:list_currencies")

    context = {"currency": currency, "form": form}
    return render(request, "replace_currency.html", context)


def delete_currency_view(request, currency_id):
    currency = Currency.objects.filter(pk=currency_id).first()
    if not currency:
        raise Http404("Currency does not exist")

    currency.delete()
    return redirect("invoices:list_currencies")
