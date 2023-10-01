import decimal

from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from num2words import num2words
from xhtml2pdf import pisa

from invoices.forms import InvoiceBuyForm, InvoiceFilterForm, InvoiceSellForm
from invoices.models import Invoice


def index_view(request):
    return render(request, "index.html")


@login_required
def list_invoices_view(request):
    invoices_list = Invoice.objects.filter(user=request.user)

    filter_form = InvoiceFilterForm(request.GET)
    if filter_form.is_valid():
        invoices_list = filter_form.get_filtered_invoices(invoices_list)

    paginator = Paginator(invoices_list, 10)
    page = request.GET.get("page")
    try:
        invoices = paginator.page(page)
    except PageNotAnInteger:
        invoices = paginator.page(1)
    except EmptyPage:
        invoices = paginator.page(paginator.num_pages)

    context = {
        "invoices": invoices,
        "filter_form": filter_form,
        "current_module": "invoices",
    }
    return render(request, "invoices/list_invoices.html", context)


@login_required
def detail_invoice_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)

    if invoice.user != request.user:
        raise Http404(_("Invoice does not exist"))

    context = {"invoice": invoice}
    if invoice.invoice_type == Invoice.INVOICE_SALES:
        return render(request, "invoices/detail_sell_invoice.html", context)
    else:
        return render(request, "invoices/detail_buy_invoice.html", context)


@login_required
def create_sell_invoice_view(request):
    if request.method != "POST":
        form = InvoiceSellForm(current_user=request.user)
    else:
        form = InvoiceSellForm(data=request.POST, current_user=request.user)

        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.invoice_type = Invoice.INVOICE_SALES
            invoice.user = request.user

            invoice.save()

            return redirect("invoices:list_invoices")

    context = {"form": form}
    return render(request, "invoices/create_sell_invoice.html", context)


@login_required
def create_buy_invoice_view(request):
    if request.method != "POST":
        form = InvoiceBuyForm(current_user=request.user)
    else:
        form = InvoiceBuyForm(data=request.POST, current_user=request.user)

        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.invoice_type = Invoice.INVOICE_PURCHASE
            invoice.user = request.user

            invoice.save()

            return redirect("invoices:list_invoices")

    context = {"form": form}
    return render(request, "invoices/create_buy_invoice.html", context)


@login_required
def replace_sell_invoice_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)

    if invoice.user != request.user:
        raise Http404(_("Invoice does not exist"))

    if request.method != "POST":
        form = InvoiceSellForm(instance=invoice, current_user=request.user)
    else:
        form = InvoiceSellForm(
            instance=invoice, data=request.POST, current_user=request.user
        )

        if form.is_valid():
            form.save()

            return redirect("invoices:detail_invoice", invoice.pk)

    context = {"invoice": invoice, "form": form}
    return render(request, "invoices/replace_invoice.html", context)


@login_required
def delete_invoice_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)

    if invoice.user != request.user:
        raise Http404(_("Invoice does not exist"))

    invoice.delete()

    return redirect("invoices:list_invoices")


@login_required
def pdf_invoice_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    if invoice.user != request.user:
        raise Http404(_("Invoice does not exist"))

    items = invoice.items.all()

    template_path = "invoices/pdf_invoice.html"

    gross_whole = invoice.gross_amount.quantize(decimal.Decimal("1"))
    gross_whole_amount = num2words(gross_whole, lang="pl")
    gross_frac_amount = num2words(int(invoice.gross_amount - gross_whole), lang="pl")

    context = {
        "invoice": invoice,
        "items": items,
        "gross_whole_amount": gross_whole_amount,
        "gross_frac_amount": gross_frac_amount,
    }

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'filename="invoice.pdf"'

    html = render_to_string(template_path, context)

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("We had some errors <pre>" + html + "</pre>")
    return response
