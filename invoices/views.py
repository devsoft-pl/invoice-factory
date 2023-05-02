import decimal

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import get_template, render_to_string
from num2words import num2words
from xhtml2pdf import pisa

from companies.models import Company
from invoices.forms import InvoiceForm
from invoices.models import Invoice
from items.models import Item


def index_view(requeste):
    return render(requeste, "index.html")


@login_required
def list_invoices_view(request):
    invoices = Invoice.objects.filter(user=request.user)

    context = {"invoices": invoices}
    return render(request, "invoices/list_invoices.html", context)


@login_required
def detail_invoice_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)

    if invoice.user != request.user:
        raise Http404("Invoice does not exist")

    context = {"invoice": invoice}
    return render(request, "invoices/detail_invoice.html", context)


@login_required
def create_invoice_view(request, create_my_invoice=False):
    if request.method != "POST":
        form = InvoiceForm(current_user=request.user)
    else:
        form = InvoiceForm(data=request.POST, current_user=request.user)

        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.user = request.user

            if create_my_invoice:
                invoice.is_my_invoice = True

            invoice.save()

            if create_my_invoice:
                return redirect("users:detail_user", request.user.pk)

            return redirect("invoices:list_invoices")

    context = {"form": form}
    return render(request, "invoices/create_invoice.html", context)


@login_required
def replace_invoice_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)

    if invoice.user != request.user:
        raise Http404("Invoice does not exist")

    if request.method != "POST":
        form = InvoiceForm(instance=invoice, current_user=request.user)
    else:
        form = InvoiceForm(
            instance=invoice, data=request.POST, current_user=request.user
        )

        if form.is_valid():
            form.save()

            if invoice.is_my_invoice:
                return redirect("users:detail_user", request.user.pk)

            return redirect("invoices:detail_invoice", invoice.pk)

    context = {"invoice": invoice, "form": form}
    return render(request, "invoices/replace_invoice.html", context)


@login_required
def delete_invoice_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)

    if invoice.user != request.user:
        raise Http404("Invoice does not exist")

    invoice.delete()

    if invoice.is_my_invoice:
        return redirect("users:detail_user", request.user.pk)

    return redirect("invoices:list_invoices")


@login_required
def pdf_invoice_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    company = Company.objects.filter(user=request.user, is_my_company=True).first()
    items = Item.objects.filter(user=request.user)

    if invoice.user != request.user:
        raise Http404("Invoice does not exist")

    template_path = "invoices/pdf_invoice.html"

    gross_whole = invoice.gross_amount.quantize(decimal.Decimal("1"))
    gross_whole_amount = num2words(gross_whole, lang="pl")
    gross_frac_amount = num2words(invoice.gross_amount - gross_whole, lang="pl")

    context = {
        "invoice": invoice,
        "company": company,
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
