from decimal import Decimal


def get_sum_invoices_per_month(invoices):
    sum_per_month = dict(
        [str(invoice["month"]), invoice["sum"]] for invoice in invoices
    )
    invoices = [
        {"month": month, "sum": sum_per_month.get(str(month), Decimal("0.00"))}
        for month in range(1, 13)
    ]

    return invoices
