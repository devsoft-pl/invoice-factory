from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import get_template
from xhtml2pdf import pisa

from invoices.forms import CompanyForm, CurrencyForm, InvoiceForm
from invoices.models import Invoice


def index_view(requeste):
    return render(requeste, "index.html")


def list_invoices_view(request):
    invoices = Invoice.objects.all()
    context = {"invoices": invoices}
    return render(request, "list_invoices.html", context)


def detail_invoice_view(request, invoice_id):
    invoice = Invoice.objects.filter(pk=invoice_id).first()
    if not invoice:
        raise Http404("Invoice does not exist")
    context = {"invoice": invoice}
    return render(request, "detail_invoice.html", context)


def create_invoice_view(request):
    if request.method != "POST":
        form = InvoiceForm()
    else:
        form = InvoiceForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect("invoices:list_invoices")

    context = {"form": form}
    return render(request, "create_invoice.html", context)


def create_company_view(request):
    if request.method != "POST":
        initial = {"next": request.GET.get("next")}
        form = CompanyForm(initial=initial)
    else:
        form = CompanyForm(data=request.POST)
        if form.is_valid():
            form.save()

            next_url = form.cleaned_data["next"]
            if next_url:
                return redirect(next_url)

    context = {"form": form}
    return render(request, "create_company.html", context)


def create_currency_view(request):
    if request.method != "POST":
        initial = {"next": request.GET.get("next")}
        form = CurrencyForm(initial=initial)
    else:
        form = CurrencyForm(data=request.POST)
        if form.is_valid():
            form.save()

            next_url = form.cleaned_data["next"]
            if next_url:
                return redirect(next_url)

    context = {"form": form}
    return render(request, "create_currency.html", context)


def replace_invoice_view():
    pass


def update_invoice_view():
    pass


def delete_invoice_view(request, invoice_id):
    invoice = Invoice.objects.filter(pk=invoice_id).first()
    if not invoice:
        raise Http404("Invoice does not exist")
    context = {"invoice": invoice}
    invoice.pop()
    invoice.save()
    return render(request, "delete_invoice.html", context)


def pdf_invoice_view(request):
    template_path = "pdf.html"
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
