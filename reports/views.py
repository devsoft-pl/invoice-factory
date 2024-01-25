from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models.functions import ExtractMonth
from django.shortcuts import render

from invoices.models import Invoice
from reports.forms import ReportFilterForm


@login_required
def list_reports_view(request):
    net_invoices = list(
        Invoice.objects.filter(invoice_type=Invoice.INVOICE_SALES)
        .annotate(month=ExtractMonth("sale_date"))
        .values("month")
        .annotate(net_sum=Sum("net_amount"))
    )

    net_sum_per_month = dict(
        [str(invoice["month"]), invoice["net_sum"]] for invoice in net_invoices
    )
    net_invoices = [
        {"month": month, "net_sum": net_sum_per_month.get(str(month), 0)}
        for month in range(1, 13)
    ]

    total_net_sum = sum(net_sum_per_month.values())

    gross_invoices = list(
        Invoice.objects.filter(invoice_type=Invoice.INVOICE_SALES)
        .annotate(month=ExtractMonth("sale_date"))
        .values("month")
        .annotate(gross_sum=Sum("gross_amount"))
    )

    gross_sum_per_month = dict(
        [str(invoice["month"]), invoice["gross_sum"]] for invoice in gross_invoices
    )
    gross_invoices = [
        {"month": month, "gross_sum": gross_sum_per_month.get(str(month), 0)}
        for month in range(1, 13)
    ]

    total_gross_sum = sum(gross_sum_per_month.values())

    filter_form = ReportFilterForm(request.GET)
    if filter_form.is_valid():
        revenue_type = filter_form.cleaned_data["revenue_type"]
        if revenue_type == ReportFilterForm.NETTO:
            context = {
                "net_invoices": net_invoices,
                "total_net_sum": total_net_sum,
                "filter_form": filter_form,
                "current_module": "reports",
            }
        elif revenue_type == ReportFilterForm.GROSS:
            context = {
                "gross_invoices": gross_invoices,
                "total_gross_sum": total_gross_sum,
                "filter_form": filter_form,
                "current_module": "reports",
            }
        else:
            context = {
                "net_invoices": net_invoices,
                "total_net_sum": total_net_sum,
                "gross_invoices": gross_invoices,
                "total_gross_sum": total_gross_sum,
                "invoices": zip(net_invoices, gross_invoices),
                "filter_form": filter_form,
                "current_module": "reports",
            }
    else:
        context = {
            "net_invoices": net_invoices,
            "total_net_sum": total_net_sum,
            "gross_invoices": gross_invoices,
            "total_gross_sum": total_gross_sum,
            "invoices": zip(net_invoices, gross_invoices),
            "filter_form": filter_form,
            "current_module": "reports",
        }
        breakpoint()
    return render(request, "reports/list_reports.html", context)
