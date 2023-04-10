from django.http import Http404
from django.shortcuts import redirect, render

from vat_rates.forms import VatRateForm
from vat_rates.models import VatRate


def list_vates_view(request):
    vat_rates = VatRate.objects.all()
    context = {"vat_rates": vat_rates}
    return render(request, "list_vates.html", context)


def detail_vat_view(request, vat_id):
    vat_rate = VatRate.objects.filter(pk=vat_id).first()
    if not vat_rate:
        raise Http404("Invoice does not exist")

    context = {"vat_rate": vat_rate}
    return render(request, "detail_vat.html", context)


def create_vat_view(request):
    if request.method != "POST":
        initial = {"next": request.GET.get("next")}
        form = VatRateForm(initial=initial)
    else:
        form = VatRateForm(data=request.POST)
        if form.is_valid():
            form.save()

            next_url = form.cleaned_data["next"]
            if next_url:
                return redirect(next_url)

            return redirect("vat_rates:list_vates")

    context = {"form": form}
    return render(request, "create_vat.html", context)


def replace_vat_view(request, vat_rate_id):
    vat_rate = VatRate.objects.filter(pk=vat_rate_id).first()
    if not vat_rate:
        raise Http404("Vat rate does not exist")

    if request.method != "POST":
        form = VatRateForm(instance=vat_rate)
    else:
        form = VatRateForm(instance=vat_rate, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect("vat_rates:list_vates")

    context = {"vat_rate": vat_rate, "form": form}
    return render(request, "replace_vat.html", context)
