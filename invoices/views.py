from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import get_template
from xhtml2pdf import pisa

from invoices.forms import InvoiceForm
from invoices.models import Invoice


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
def create_invoice_view(request):
    if request.method != "POST":
        form = InvoiceForm()
    else:
        form = InvoiceForm(data=request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.user = request.user
            invoice.save()
            return redirect("invoices:list_invoices")

    context = {"form": form}
    return render(request, "invoices/create_invoice.html", context)


@login_required
def replace_invoice_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)

    if invoice.user != request.user:
        raise Http404("Invoice does not exist")

    if request.method != "POST":
        form = InvoiceForm(instance=invoice)
    else:
        form = InvoiceForm(instance=invoice, data=request.POST)
        if form.is_valid():
            form.save()

            return redirect("invoices:list_invoices")

    context = {"invoice": invoice, "form": form}
    return render(request, "invoices/replace_invoice.html", context)


@login_required
def delete_invoice_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)

    if invoice.user != request.user:
        raise Http404("Invoice does not exist")

    invoice.delete()
    return redirect("invoices:list_invoices")


@login_required
def pdf_invoice_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)

    if invoice.user != request.user:
        raise Http404("Invoice does not exist")

    template_path = "invoices/pdf_invoice.html"
    context = {"invoice": invoice}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'filename="invoice.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(html, dest=response)
    # if error then show some funny view
    if pisa_status.err:
        return HttpResponse("We had some errors <pre>" + html + "</pre>")
    return response
