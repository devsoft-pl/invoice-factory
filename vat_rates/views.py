from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from vat_rates.forms import VatRateForm
from vat_rates.models import VatRate


@login_required
def list_vates_view(request):
    vat_rates = VatRate.objects.filter(user=request.user)
    context = {"vat_rates": vat_rates}
    return render(request, "vat_rates/list_vates.html", context)


@login_required
def detail_vat_view(request, vat_id):
    vat_rate = get_object_or_404(VatRate, pk=vat_id)

    if vat_rate.user != request.user:
        raise Http404("Vat rate does not exist")

    context = {"vat_rate": vat_rate}
    return render(request, "vat_rates/detail_vat.html", context)


@login_required
def create_vat_view(request):
    if request.method != "POST":
        initial = {"next": request.GET.get("next")}
        form = VatRateForm(initial=initial)
    else:
        form = VatRateForm(data=request.POST)
        if form.is_valid():
            vat_rate = form.save(commit=False)
            vat_rate.user = request.user
            vat_rate.save()

            next_url = form.cleaned_data["next"]
            if next_url:
                return redirect(next_url)

            return redirect("vat_rates:list_vates")

    context = {"form": form}
    return render(request, "vat_rates/create_vat.html", context)


@login_required
def replace_vat_view(request, vat_id):
    vat_rate = get_object_or_404(VatRate, pk=vat_id)

    if vat_rate.user != request.user:
        raise Http404("Vat rate does not exist")

    if request.method != "POST":
        form = VatRateForm(instance=vat_rate)
    else:
        form = VatRateForm(instance=vat_rate, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect("vat_rates:list_vates")

    context = {"vat_rate": vat_rate, "form": form}
    return render(request, "vat_rates/replace_vat.html", context)


@login_required
def delete_vat_view(request, vat_id):
    var_rate = get_object_or_404(VatRate, pk=vat_id)

    if var_rate.user != request.user:
        raise Http404("Vat rate does not exist")

    var_rate.delete()
    return redirect("vat_rates:list_vates")
