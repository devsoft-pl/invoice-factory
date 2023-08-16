import calendar
import logging
from datetime import datetime, timedelta

from base.celery import app
from invoices.models import Invoice

logger = logging.getLogger(__name__)


@app.task(name="create_invoices_for_recurring")
def create_invoices_for_recurring():
    logger.info("Trying to create invoices recurring")

    invoices = Invoice.objects.filter(is_recurring=True)

    date = datetime.today()
    payment_date = date + timedelta(days=7)
    month_range = calendar.monthrange(date.year, date.month)
    last_day = month_range[1]

    if last_day != date.day:
        return

    for invoice in invoices:
        new_invoice = Invoice.objects.create(
            invoice_number=f"{date.month}/{date.year}",
            create_date=date,
            sale_date=date,
            payment_date=payment_date,
        )

        for item in invoice.items.all():
            item.pk = None
            item.invoice = new_invoice
            item.save()
