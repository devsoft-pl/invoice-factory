from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
from xhtml2pdf import pisa

from invoices.models import Invoice


def invoices_view(request):
    invoices = Invoice.objects.all()
    context = {"invoices": invoices}
    return render(request, "invoices.html", context)


def detail_invoice_view(request, invoice_id):
    invoice = Invoice.objects.filter(pk=invoice_id).first()
    if not invoice:
        raise Http404("Invoice does not exist")
    context = {"invoice": invoice}
    return render(request, "detail_invoice.html", context)


def create_invoice_view():
    pass


def replace_invoice_view():
    pass


def update_invoice_view():
    pass


def delete_invoice_view():
    pass


def invoice_pdf_view(request):
    template_path = "invoice.html"
    context = {"myvar": "this is your template context"}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'filename="faktura.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(html, dest=response)
    # if error then show some funny view
    if pisa_status.err:
        return HttpResponse("We had some errors <pre>" + html + "</pre>")
    return response
