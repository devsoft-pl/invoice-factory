from datetime import datetime
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render

from invoices.models import Invoice, Year
from reports.forms import ReportFilterForm
from reports.utils import get_sum_invoices_per_month


@login_required
def list_reports_view(request):
    filter_form = ReportFilterForm(request.GET)

    year = Year.objects.first() or Year(year=datetime.now().year)

    if filter_form.is_valid():
        if filter_form.cleaned_data["year"]:
            year = filter_form.cleaned_data["year"]

    net_invoices = list(
        Invoice.objects.filter(
            Q(company__user=request.user, sale_date__year=year.year, is_recurring=False)
            | Q(
                person__user=request.user, sale_date__year=year.year, is_recurring=False
            )
        )
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
        Invoice.objects.filter(
            Q(company__user=request.user, sale_date__year=year.year, is_recurring=False)
            | Q(
                person__user=request.user, sale_date__year=year.year, is_recurring=False
            )
        )
        .sales()
        .with_months()
        .with_sum("gross_amount")
    )

    gross_invoices = get_sum_invoices_per_month(gross_invoices)
    gross_sum_per_month = dict(
        [str(invoice["month"]), invoice["sum"]] for invoice in gross_invoices
    )
    total_gross_sum = sum(gross_sum_per_month.values())

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

    context: dict[str, int | str | list[dict[str, int | str | Decimal]] | list] = {
        "filter_form": filter_form,
        "current_module": "reports",
    }
    context.update(extra_context)
    return render(request, "reports/list_reports.html", context)
