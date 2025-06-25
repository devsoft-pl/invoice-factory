import calendar
import logging
import tempfile
from datetime import datetime, timedelta

from django.utils.translation import gettext_lazy as _
from xhtml2pdf import pisa

from base.celery import app
from invoices.forms import is_last_day_of_month
from invoices.models import Invoice
from invoices.utils import create_recurrent_invoices
from summary_recipients.models import SummaryRecipient

logger = logging.getLogger(__name__)


@app.task(name="create_invoices_for_recurring")
def create_invoices_for_recurring():
    today = datetime.today()

    month_range = calendar.monthrange(today.year, today.month)
    last_day = month_range[1]

    invoices = Invoice.objects.filter(is_recurring=True)
    if today.day == last_day:
        invoices = invoices.filter(is_last_day=True)
    else:
        invoices = invoices.filter(sale_date__day=today.day, is_last_day=False)

    create_recurrent_invoices(invoices)


@app.task(name="send_monthly_summary_to_recipients")
def send_monthly_summary_to_recipients():
    logger.info("Trying to send summary to recipients")

    today = datetime.today()
    is_last_day = is_last_day_of_month(today)
    summary_date = today - timedelta(days=today.day)

    if is_last_day:
        summary_recipients = SummaryRecipient.objects.filter(is_last_day=True)
    else:
        summary_recipients = SummaryRecipient.objects.filter(day=today.day)

    for summary_recipient in summary_recipients:
        company = summary_recipient.company
        invoices = Invoice.objects.filter(
            company=company,
            create_date__month=summary_date.month,
            create_date__year=summary_date.year,
            is_recurring=False,
        )

        files = []

        for invoice in invoices:
            html = invoice.get_html_for_pdf()

            with tempfile.NamedTemporaryFile(suffix=".pdf") as invoice_file:
                pisa.CreatePDF(html, dest=invoice_file)

                invoice_file.seek(0)

                files.append(
                    {
                        "name": f"{invoice.invoice_number.replace('/', '-')}.pdf",
                        "content": invoice_file.read(),
                    }
                )

        subject = _("Month summary")
        content = _(
            "A monthly summary has been created for company\n"
            "Best regards,\n"
            "Invoice-Factory"
        )

        summary_recipient.send_email(subject, content, files)

        if summary_recipient.final_call:
            for invoice in invoices:
                invoice.is_settled = True
                invoice.save()
