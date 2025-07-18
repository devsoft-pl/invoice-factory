from datetime import datetime
from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
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

    if invoice.company:
        if invoice.company.user != request.user:
            raise Http404(_("Invoice does not exist"))
    elif invoice.person:
        if invoice.person.user != request.user:
            raise Http404(_("Invoice does not exist"))
    else:
        raise Exception(_("This should not have happened"))

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
def create_sell_person_to_client_invoice_view(request):
    if request.method != "POST":
        form = InvoiceSellPersonToClientForm(current_user=request.user)
    else:
        form = InvoiceSellPersonToClientForm(
            current_user=request.user, data=request.POST
        )

        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.invoice_type = Invoice.INVOICE_SALES

            invoice.save()

            return redirect("invoices:list_invoices")

    context = {"form": form}
    return render(
        request, "invoices/create_sell_person_to_client_invoice.html", context
    )


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


@login_required
def duplicate_company_invoice_view(request, invoice_id):
    today = datetime.today()
    month = get_right_month_format(today.month)

    queryset = Invoice.objects.select_related(
        "company", "person", "company__user"
    ).prefetch_related("items")
    invoice = get_object_or_404(queryset, pk=invoice_id)

    if invoice.company.user != request.user or invoice.is_recurring:
        raise Http404(_("Invoice does not exist"))

    if invoice.person:
        form_klass = InvoiceSellPersonForm
    else:
        form_klass = InvoiceSellForm

    new_instance: Invoice = clone(invoice)
    max_invoice_number = get_max_invoice_number(invoice.company, invoice.person)
    new_instance.invoice_number = f"{max_invoice_number}/{month}/{today.year}"
    new_instance.sale_date = today
    new_instance.create_date = today
    new_instance.payment_date = today
    new_instance.is_settled = False
    new_instance.is_paid = False
    new_instance.save()
    for item in invoice.items.all():
        new_item = clone(item)
        new_item.invoice = new_instance
        new_item.save()

    form = form_klass(instance=new_instance, current_user=request.user)

    context = {"invoice": new_instance, "form": form, "duplicate": True}
    return render(request, "invoices/replace_sell_invoice.html", context)


@login_required
def duplicate_individual_invoice_view(request, invoice_id):
    today = datetime.today()
    month = get_right_month_format(today.month)

    queryset = Invoice.objects.select_related(
        "company", "person", "person__user"
    ).prefetch_related("items")
    invoice = get_object_or_404(queryset, pk=invoice_id)

    if invoice.person:
        if invoice.person.user != request.user or invoice.is_recurring:
            raise Http404(_("Invoice does not exist"))

    new_instance: Invoice = clone(invoice)
    max_invoice_number = get_max_invoice_number(invoice.company, invoice.person)
    new_instance.invoice_number = f"{max_invoice_number}/{month}/{today.year}"
    new_instance.sale_date = today
    new_instance.create_date = today
    new_instance.payment_date = today
    new_instance.is_settled = False
    new_instance.is_paid = False
    new_instance.save()
    for item in invoice.items.all():
        new_item = clone(item)
        new_item.invoice = new_instance
        new_item.save()

    form = InvoiceSellPersonToClientForm(
        instance=new_instance, current_user=request.user
    )

    context = {"invoice": new_instance, "form": form, "duplicate": True}
    return render(
        request, "invoices/replace_sell_person_to_client_invoice.html", context
    )


@login_required
def replace_sell_invoice_view(request, invoice_id, create_correction=False):
    queryset = Invoice.objects.select_related("company", "person", "company__user")
    invoice = get_object_or_404(queryset, pk=invoice_id)

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
def replace_sell_person_to_client_invoice_view(
    request, invoice_id, create_correction=False
):
    queryset = Invoice.objects.select_related("person", "person__user")
    invoice = get_object_or_404(queryset, pk=invoice_id)

    if invoice.person:
        if invoice.person.user != request.user or (
            invoice.is_settled and not create_correction
        ):
            raise Http404(_("Invoice does not exist"))
    else:
        raise Exception(_("This should not have happened"))

    if create_correction:
        new_instance = clone(invoice)
        new_instance.pk = None
        new_instance.is_recurring = False
        new_instance.is_settled = False
        new_instance.invoice_number = create_correction_invoice_number(new_instance)
    else:
        new_instance = invoice

    if request.method != "POST":
        form = InvoiceSellPersonToClientForm(
            instance=new_instance, current_user=request.user
        )
    else:
        form = InvoiceSellPersonToClientForm(
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
    return render(
        request, "invoices/replace_sell_person_to_client_invoice.html", context
    )


@login_required
def replace_buy_invoice_view(request, invoice_id):
    queryset = Invoice.objects.select_related("company", "company__user")
    invoice = get_object_or_404(queryset, pk=invoice_id)

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
    queryset = Invoice.objects.select_related(
        "company", "company__user", "person", "person__user"
    )
    invoice = get_object_or_404(queryset, pk=invoice_id)

    if invoice.company:
        if invoice.company.user != request.user:
            raise Http404(_("Invoice does not exist"))
    elif invoice.person:
        if invoice.person.user != request.user:
            raise Http404(_("Invoice does not exist"))
    else:
        raise Exception(_("This should not have happened"))

    invoice.delete()

    return redirect("invoices:list_invoices")


@login_required
def pdf_invoice_view(request, invoice_id):
    queryset = Invoice.objects.select_related(
        "company", "company__user", "person", "person__user"
    ).prefetch_related("items")
    invoice = get_object_or_404(queryset, pk=invoice_id)

    if invoice.company:
        if invoice.company.user != request.user:
            raise Http404(_("Invoice does not exist"))
    elif invoice.person:
        if invoice.person.user != request.user:
            raise Http404(_("Invoice does not exist"))
    else:
        raise Exception(_("This should not have happened"))

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'filename="invoice.pdf"'

    html = invoice.get_html_for_pdf()

    def link_callback(uri, rel):
        return str(Path(rel) / "invoices" / uri.lstrip("/"))

    pisa_status = pisa.CreatePDF(html, dest=response, link_callback=link_callback)

    if pisa_status.err:
        return HttpResponse("We had some errors <pre>" + html + "</pre>")
    return response
