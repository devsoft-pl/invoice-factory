import calendar
import logging
import tempfile
from datetime import datetime, timedelta

from django.utils.translation import gettext as _
from xhtml2pdf import pisa

from base.celery import app
from companies.models import Company
from invoices.models import Invoice
from summary_recipients.models import SummaryRecipient

logger = logging.getLogger(__name__)


@app.task(name="create_invoices_for_recurring")
def create_invoices_for_recurring():
    logger.info("Trying to create invoices recurring")

    invoices = Invoice.objects.filter(is_recurring=True)
    date = datetime.today()

    month_range = calendar.monthrange(date.year, date.month)
    last_day = month_range[1]

    if last_day != date.day:
        return

    for invoice in invoices:
        payment_date = date + timedelta(
            days=(invoice.payment_date - invoice.sale_date).days
        )
        new_invoice = Invoice.objects.create(
            invoice_number=f"{date.month}/{date.year}",
            invoice_type=Invoice.INVOICE_SALES,
            company=invoice.company,
            is_recurring=False,
            is_settled=False,
            create_date=date,
            sale_date=date,
            payment_date=payment_date,
            payment_method=invoice.payment_method,
            currency=invoice.currency,
            account_number=invoice.account_number,
            client=invoice.client,
            person=invoice.person,
            settlement_date=None,
        )

        for item in invoice.items.all():
            item.pk = None
            item.invoice = new_invoice
            item.save()

        subject = _("New recurring invoice %(nr)s") % {"nr": new_invoice.invoice_number}
        content = _(
            "A new recurring invoice has been created\n"
            "Best regards,\n"
            "Invoice Manager"
        )

        html = new_invoice.get_html_for_pdf()

        # create and open temporary file as invoice_file
        with tempfile.NamedTemporaryFile(suffix=".pdf") as invoice_file:
            # write rendered PDF to invoice_file
            pisa.CreatePDF(html, dest=invoice_file)

            # go to beginning of file
            invoice_file.seek(0)

            files = [
                {
                    "name": f"{new_invoice.invoice_number.replace('/', '-')}.pdf",
                    "content": invoice_file.read(),
                }
            ]
            new_invoice.company.user.send_email(subject, content, files)


@app.task(name="send_monthly_summary_to_recipients")
def send_monthly_summary_to_recipients():
    logger.info("Trying to send summary to recipients")

    today = datetime.today()
    summary_date = today - timedelta(days=today.day)

    companies = Company.objects.filter(is_my_company=True)

    for company in companies:
        invoices = Invoice.objects.filter(
            company=company,
            create_date__month=summary_date.month,
            create_date__year=summary_date.year,
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
            "Invoice Manager"
        )

        summary_recipients = SummaryRecipient.objects.filter(
            day=today.day, company=company
        )

        for summary_recipient in summary_recipients:
            summary_recipient.send_email(subject, content, files)

            if summary_recipient.final_call:
                for invoice in invoices:
                    invoice.is_settled = True
                    invoice.save()
