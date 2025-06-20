from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from invoices.models import Invoice
from items.forms import ItemForm
from items.models import Item


@login_required
def create_item_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)

    if request.method != "POST":
        form = ItemForm(current_user=request.user)
    else:
        form = ItemForm(data=request.POST, current_user=request.user)

        if form.is_valid():
            item = form.save(commit=False)
            item.invoice = invoice

            item.save()

            return redirect("invoices:detail_invoice", invoice.pk)

    context = {"form": form, "invoice": invoice}
    return render(request, "items/create_item.html", context)


@login_required
def replace_item_view(request, item_id):
    item = get_object_or_404(
        Item.objects.select_related(
            "invoice__company__user", "invoice__person__user", "invoice"
        ),
        pk=item_id,
    )

    if item.invoice.company:
        if item.invoice.company.user != request.user:
            raise Http404(_("Item does not exist"))
    elif item.invoice.person:
        if item.invoice.person.user != request.user:
            raise Http404(_("Item does not exist"))
    else:
        raise Exception(_("This should not have happened"))

    if request.method != "POST":
        form = ItemForm(instance=item, current_user=request.user)
    else:
        form = ItemForm(instance=item, data=request.POST, current_user=request.user)

        if form.is_valid():
            form.save()

            return redirect("invoices:detail_invoice", item.invoice.pk)

    context = {"item": item, "form": form}
    return render(request, "items/replace_item.html", context)


@login_required
def delete_item_view(request, item_id):
    item = get_object_or_404(
        Item.objects.select_related(
            "invoice__company__user", "invoice__person__user", "invoice"
        ),
        pk=item_id,
    )

    if item.invoice.company:
        if item.invoice.company.user != request.user:
            raise Http404(_("Item does not exist"))
    elif item.invoice.person:
        if item.invoice.person.user != request.user:
            raise Http404(_("Item does not exist"))
    else:
        raise Exception(_("This should not have happened"))

    item.delete()

    return redirect("invoices:detail_invoice", item.invoice.pk)
