import copy

from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from xhtml2pdf import pisa

from invoices.forms import (InvoiceBuyForm, InvoiceFilterForm,
                            InvoiceRecurringForm, InvoiceSellForm,
                            InvoiceSellPersonForm)
from invoices.models import CorrectionInvoiceRelation, Invoice


def index_view(request):
    return render(request, "index.html")


@login_required
def list_invoices_view(request):
    invoices_list = Invoice.objects.filter(company__user=request.user)

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

    if invoice.company.user != request.user:
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

            invoice.save()

            return redirect("invoices:list_invoices")

    context = {"form": form}
    return render(request, "invoices/create_sell_invoice.html", context)


@login_required
def create_sell_person_invoice_view(request):
    if request.method != "POST":
        form = InvoiceSellPersonForm(current_user=request.user)
    else:
        form = InvoiceSellPersonForm(current_user=request.user, data=request.POST)

        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.invoice_type = Invoice.INVOICE_SALES

            invoice.save()

            return redirect("invoices:list_invoices")

    context = {"form": form}
    return render(request, "invoices/create_sell_person_invoice.html", context)


@login_required
def create_buy_invoice_view(request):
    if request.method != "POST":
        form = InvoiceBuyForm(current_user=request.user)
    else:
        form = InvoiceBuyForm(
            data=request.POST, files=request.FILES, current_user=request.user
        )

        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.invoice_type = Invoice.INVOICE_PURCHASE

            invoice.save()

            return redirect("invoices:list_invoices")

    context = {"form": form}
    return render(request, "invoices/create_buy_invoice.html", context)


def clone(instance):
    cloned = copy.copy(instance)
    cloned.pk = None
    try:
        delattr(cloned, "_prefetched_objects_cache")
    except AttributeError:
        pass
    return cloned


def create_correction_invoice_number(invoice: Invoice):
    invoice_number_parts = invoice.invoice_number.split("/")
    invoice_number_parts.insert(3, "korekta")
    return "/".join(invoice_number_parts)


@login_required
def replace_sell_invoice_view(request, invoice_id, create_correction=False):
    invoice = get_object_or_404(Invoice, pk=invoice_id)

    if invoice.company.user != request.user or (
        invoice.is_settled and not create_correction
    ):
        raise Http404(_("Invoice does not exist"))

    if invoice.person:
        form_klass = InvoiceSellPersonForm
    else:
        form_klass = InvoiceSellForm

    if create_correction:
        new_instance = clone(invoice)
        new_instance.pk = None
        new_instance.is_recurring = False
        new_instance.is_settled = False
        new_instance.invoice_number = create_correction_invoice_number(new_instance)
    else:
        new_instance = invoice

    if request.method != "POST":
        form = form_klass(instance=new_instance, current_user=request.user)
    else:
        form = form_klass(
            instance=new_instance,
            data=request.POST,
            files=request.FILES,
            current_user=request.user,
            create_correction=create_correction,
        )

        if form.is_valid():
            new_invoice = form.save(commit=False)
            new_invoice.save()
            if create_correction:
                CorrectionInvoiceRelation.objects.get_or_create(
                    invoice=invoice, correction_invoice=new_invoice
                )

            if create_correction:
                return redirect("invoices:list_invoices")

            return redirect("invoices:detail_invoice", invoice.pk)

    context = {"invoice": invoice, "form": form, "create_correction": create_correction}
    return render(request, "invoices/replace_sell_invoice.html", context)


@login_required
def replace_buy_invoice_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)

    if invoice.company.user != request.user:
        raise Http404(_("Invoice does not exist"))

    if request.method != "POST":
        form = InvoiceBuyForm(instance=invoice, current_user=request.user)
    else:
        form = InvoiceBuyForm(
            instance=invoice, data=request.POST, current_user=request.user
        )

        if form.is_valid():
            form.save()

            return redirect("invoices:detail_invoice", invoice.pk)

    context = {"invoice": invoice, "form": form}
    return render(request, "invoices/replace_buy_invoice.html", context)


@login_required
def delete_invoice_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)

    if invoice.company.user != request.user:
        raise Http404(_("Invoice does not exist"))

    invoice.delete()

    return redirect("invoices:list_invoices")


@login_required
def pdf_invoice_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)

    if invoice.company.user != request.user:
        raise Http404(_("Invoice does not exist"))

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'filename="invoice.pdf"'

    html = invoice.get_html_for_pdf()

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("We had some errors <pre>" + html + "</pre>")
    return response
