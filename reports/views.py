from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from invoices.models import Invoice
from reports.forms import ReportFilterForm


def get_sum_invoices_per_month(invoices):
    sum_per_month = dict(
        [str(invoice["month"]), invoice["sum"]] for invoice in invoices
    )
    invoices = [
        {"month": month, "sum": sum_per_month.get(str(month), Decimal("0.00"))}
        for month in range(1, 13)
    ]

    return invoices


@login_required
def list_reports_view(request):
    net_invoices = list(
        Invoice.objects.filter(company__user=request.user)
        .sales()
        .with_months()
        .with_sum("net_amount")
    )
    net_invoices = get_sum_invoices_per_month(net_invoices)

    net_sum_per_month = dict(
        [str(invoice["month"]), invoice["sum"]] for invoice in net_invoices
    )
    total_net_sum = sum(net_sum_per_month.values())

    gross_invoices = list(
        Invoice.objects.filter(company__user=request.user)
        .sales()
        .with_months()
        .with_sum("gross_amount")
    )
    gross_invoices = get_sum_invoices_per_month(gross_invoices)

    gross_sum_per_month = dict(
        [str(invoice["month"]), invoice["sum"]] for invoice in gross_invoices
    )
    total_gross_sum = sum(gross_sum_per_month.values())

    filter_form = ReportFilterForm(request.GET)

    extra_context = {
        "net_invoices": net_invoices,
        "total_net_sum": total_net_sum,
        "gross_invoices": gross_invoices,
        "total_gross_sum": total_gross_sum,
        "invoices": list(zip(net_invoices, gross_invoices)),
    }

    if filter_form.is_valid():
        revenue_type = filter_form.cleaned_data["revenue_type"]
        if revenue_type == ReportFilterForm.NETTO:
            extra_context = {
                "net_invoices": net_invoices,
                "total_net_sum": total_net_sum,
            }
        elif revenue_type == ReportFilterForm.GROSS:
            extra_context = {
                "gross_invoices": gross_invoices,
                "total_gross_sum": total_gross_sum,
            }

    context = {
        "filter_form": filter_form,
        "current_module": "reports",
    }
    context.update(extra_context)

    return render(request, "reports/list_reports.html", context)
