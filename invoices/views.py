from datetime import datetime
from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import transaction
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from xhtml2pdf import pisa

from invoices.forms import (
    InvoiceBuyForm,
    InvoiceFilterForm,
    InvoiceSellForm,
    InvoiceSellPersonForm,
    InvoiceSellPersonToClientForm,
)
from invoices.models import CorrectionInvoiceRelation, Invoice
from invoices.utils import (
    clone,
    create_correction_invoice_number,
    get_max_invoice_number,
    get_right_month_format,
)


def _handle_invoice_creation(request, form_class, template_name, invoice_type):
    if request.method == "POST":
        form = form_class(
            data=request.POST, files=request.FILES, current_user=request.user
        )
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.invoice_type = invoice_type
            invoice.save()
            return redirect("invoices:list_invoices")
    else:
        form = form_class(current_user=request.user)

    return render(request, template_name, {"form": form})


def _handle_invoice_replacement(
    request, invoice, form_class, template_name, create_correction=False
):
    if create_correction:
        new_instance = clone(invoice)
        new_instance.pk = None
        new_instance.is_recurring = False
        new_instance.is_settled = False
        new_instance.invoice_number = create_correction_invoice_number(new_instance)
    else:
        new_instance = invoice

    if request.method == "POST":
        form = form_class(
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
                return redirect("invoices:list_invoices")
            return redirect("invoices:detail_invoice", invoice.pk)
    else:
        form = form_class(instance=new_instance, current_user=request.user)

    context = {"invoice": invoice, "form": form, "create_correction": create_correction}
    return render(request, template_name, context)


def _handle_invoice_duplication(request, invoice, form_klass, template_name):
    today = datetime.today()
    month = get_right_month_format(today.month)

    new_instance: Invoice = clone(invoice)
    max_invoice_number = get_max_invoice_number(invoice.company, invoice.person)
    new_instance.invoice_number = f"{max_invoice_number}/{month}/{today.year}"
    new_instance.sale_date = today
    new_instance.create_date = today
    new_instance.payment_date = today
    new_instance.is_settled = False
    new_instance.is_paid = False

    with transaction.atomic():
        new_instance.save()
        for item in invoice.items.all():
            new_item = clone(item)
            new_item.invoice = new_instance
            new_item.save()
        new_instance.update_totals()

    form = form_klass(instance=new_instance, current_user=request.user)

    context = {"invoice": new_instance, "form": form, "duplicate": True}
    return render(request, template_name, context)


def index_view(request):
    return render(request, "index.html")


@login_required
def list_invoices_view(request):
    invoices_list = (
        Invoice.objects.filter(
            Q(company__user=request.user) | Q(person__user=request.user)
        )
        .select_related("company", "person", "client")
        .prefetch_related("items")
    )

    filter_form = InvoiceFilterForm(request.GET)
    if filter_form.is_valid():
        invoices_list = filter_form.get_filtered_invoices(invoices_list)

    total_invoices = invoices_list.count()

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
        "total_invoices": total_invoices,
        "filter_form": filter_form,
        "current_module": "invoices",
    }
    return render(request, "invoices/list_invoices.html", context)


@login_required
def detail_invoice_view(request, invoice_id):
    queryset = Invoice.objects.select_related(
        "company", "person", "client"
    ).prefetch_related("items")
    invoice = get_object_or_404(queryset, pk=invoice_id)

    if not invoice.is_owned_by(request.user):
        raise Http404(_("Invoice does not exist"))

    context = {"invoice": invoice}
    if invoice.invoice_type == Invoice.INVOICE_SALES:
        return render(request, "invoices/detail_sell_invoice.html", context)
    else:
        return render(request, "invoices/detail_buy_invoice.html", context)


@login_required
def create_sell_invoice_view(request):
    return _handle_invoice_creation(
        request,
        form_class=InvoiceSellForm,
        template_name="invoices/create_sell_invoice.html",
        invoice_type=Invoice.INVOICE_SALES,
    )


@login_required
def create_sell_person_invoice_view(request):
    return _handle_invoice_creation(
        request,
        form_class=InvoiceSellPersonForm,
        template_name="invoices/create_sell_person_invoice.html",
        invoice_type=Invoice.INVOICE_SALES,
    )


@login_required
def create_sell_person_to_client_invoice_view(request):
    return _handle_invoice_creation(
        request,
        form_class=InvoiceSellPersonToClientForm,
        template_name="invoices/create_sell_person_to_client_invoice.html",
        invoice_type=Invoice.INVOICE_SALES,
    )


@login_required
def create_buy_invoice_view(request):
    return _handle_invoice_creation(
        request,
        form_class=InvoiceBuyForm,
        template_name="invoices/create_buy_invoice.html",
        invoice_type=Invoice.INVOICE_PURCHASE,
    )


@login_required
def duplicate_company_invoice_view(request, invoice_id):
    queryset = Invoice.objects.select_related(
        "company", "person", "company__user"
    ).prefetch_related("items")
    invoice = get_object_or_404(queryset, pk=invoice_id)

    if not invoice.is_owned_by(request.user) or invoice.is_recurring:
        raise Http404(_("Invoice does not exist"))

    form_klass = InvoiceSellPersonForm if invoice.person else InvoiceSellForm
    template_name = "invoices/replace_sell_invoice.html"

    return _handle_invoice_duplication(request, invoice, form_klass, template_name)


@login_required
def duplicate_individual_invoice_view(request, invoice_id):
    queryset = Invoice.objects.select_related(
        "company", "person", "person__user"
    ).prefetch_related("items")
    invoice = get_object_or_404(queryset, pk=invoice_id)

    if not invoice.is_owned_by(request.user) or invoice.is_recurring:
        raise Http404(_("Invoice does not exist"))

    form_klass = InvoiceSellPersonToClientForm
    template_name = "invoices/replace_sell_person_to_client_invoice.html"

    return _handle_invoice_duplication(request, invoice, form_klass, template_name)


@login_required
def replace_sell_invoice_view(request, invoice_id, create_correction=False):
    queryset = Invoice.objects.select_related("company", "person", "company__user")
    invoice = get_object_or_404(queryset, pk=invoice_id)

    if not invoice.is_owned_by(request.user) or (
        invoice.is_settled and not create_correction
    ):
        raise Http404(_("Invoice does not exist"))

    form_klass = InvoiceSellPersonForm if invoice.person else InvoiceSellForm
    template_name = "invoices/replace_sell_invoice.html"

    return _handle_invoice_replacement(
        request, invoice, form_klass, template_name, create_correction=create_correction
    )


@login_required
def replace_sell_person_to_client_invoice_view(
    request, invoice_id, create_correction=False
):
    queryset = Invoice.objects.select_related("person", "person__user")
    invoice = get_object_or_404(queryset, pk=invoice_id)

    if not invoice.is_owned_by(request.user) or (
        invoice.is_settled and not create_correction
    ):
        raise Http404(_("Invoice does not exist"))

    form_klass = InvoiceSellPersonToClientForm
    template_name = "invoices/replace_sell_person_to_client_invoice.html"

    return _handle_invoice_replacement(
        request, invoice, form_klass, template_name, create_correction=create_correction
    )


@login_required
def replace_buy_invoice_view(request, invoice_id):
    queryset = Invoice.objects.select_related("company", "company__user")
    invoice = get_object_or_404(queryset, pk=invoice_id)

    if not invoice.is_owned_by(request.user):
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
@require_POST
def delete_invoice_view(request, invoice_id):
    queryset = Invoice.objects.select_related(
        "company", "company__user", "person", "person__user"
    )
    invoice = get_object_or_404(queryset, pk=invoice_id)

    if not invoice.is_owned_by(request.user):
        raise Http404(_("Invoice does not exist"))

    invoice.delete()

    return redirect("invoices:list_invoices")


@login_required
def pdf_invoice_view(request, invoice_id):
    queryset = Invoice.objects.select_related(
        "company", "company__user", "person", "person__user"
    ).prefetch_related("items")
    invoice = get_object_or_404(queryset, pk=invoice_id)

    if not invoice.is_owned_by(request.user):
        raise Http404(_("Invoice does not exist"))

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'filename="invoice.pdf"'

    html = invoice.get_html_for_pdf()

    def link_callback(uri, rel):
        return str(Path(rel) / "invoices" / uri.lstrip("/"))

    pisa_status = pisa.CreatePDF(html, dest=response, link_callback=link_callback)

    if pisa_status.err:
        return HttpResponse("We had some errors <pre>" + html + "</pre>")
    return response
