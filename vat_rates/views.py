from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from vat_rates.forms import VatRateForm
from vat_rates.models import VatRate


@login_required
def list_vat_rates_view(request):
    vat_list = VatRate.objects.filter(user=request.user)

    paginator = Paginator(vat_list, 10)
    page = request.GET.get("page")
    try:
        vat_rates = paginator.page(page)
    except PageNotAnInteger:
        vat_rates = paginator.page(1)
    except EmptyPage:
        vat_rates = paginator.page(paginator.num_pages)

    context = {"vat_rates": vat_rates, "current_module": "vat_rates"}
    return render(request, "vat_rates/list_vat_rates.html", context)


@login_required
def create_vat_view(request):
    if request.method != "POST":
        initial = {"next": request.GET.get("next")}
        form = VatRateForm(initial=initial, user=request.user)
    else:
        form = VatRateForm(data=request.POST, user=request.user)

        if form.is_valid():
            vat_rate = form.save(commit=False)
            vat_rate.user = request.user

            vat_rate.save()

            next_url = form.cleaned_data["next"]
            if next_url:
                return redirect(next_url)

            return redirect("vat_rates:list_vat_rates")

    context = {"form": form}
    return render(request, "vat_rates/create_vat.html", context)


@login_required
def create_vat_ajax_view(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(permitted_methods=["POST"])
    else:
        form = VatRateForm(data=request.POST, user=request.user)

        if form.is_valid():
            vat_rate = form.save(commit=False)
            vat_rate.user = request.user

            vat_rate.save()

            return JsonResponse(
                {
                    "success": True,
                    "id": vat_rate.id,
                    "name": vat_rate.rate,
                }
            )

        else:
            return JsonResponse({"success": False, "errors": form.errors})


@login_required
def replace_vat_view(request, vat_id):
    vat_rate = get_object_or_404(VatRate, pk=vat_id)

    if vat_rate.user != request.user:
        raise Http404(_("Vat rate does not exist"))

    if request.method != "POST":
        form = VatRateForm(instance=vat_rate, user=request.user)
    else:
        form = VatRateForm(instance=vat_rate, data=request.POST, user=request.user)

        if form.is_valid():
            form.save()

            return redirect("vat_rates:list_vat_rates")

    context = {"vat_rate": vat_rate, "form": form}
    return render(request, "vat_rates/replace_vat.html", context)


@login_required
def delete_vat_view(request, vat_id):
    var_rate = get_object_or_404(VatRate, pk=vat_id)

    if var_rate.user != request.user:
        raise Http404(_("Vat rate does not exist"))

    var_rate.delete()

    return redirect("vat_rates:list_vat_rates")
