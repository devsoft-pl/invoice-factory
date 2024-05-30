import calendar
import logging
import tempfile
from datetime import date, datetime, timedelta

from django.utils.translation import gettext_lazy as _
from xhtml2pdf import pisa

from base.celery import app
from companies.models import Company
from invoices.models import Invoice
from summary_recipients.models import SummaryRecipient

logger = logging.getLogger(__name__)


FIRST_INVOICE_NUMBER = 1


def get_invoice_with_max_sale_date():
    return (
        Invoice.objects.filter(invoice_type=Invoice.INVOICE_SALES, is_recurring=False)
        .order_by("-sale_date", "pk")
        .first()
    )


def get_max_invoice_number():
    max_sale_date_invoice = get_invoice_with_max_sale_date()

    current_year = date.today().year
    if (
        not max_sale_date_invoice
        or max_sale_date_invoice.sale_date.year != current_year
    ):
        return FIRST_INVOICE_NUMBER
    else:
        last_invoice_number = max_sale_date_invoice.invoice_number.split("/")[0]
        return int(last_invoice_number) + 1


def get_right_month_format(month_number):
    if month_number in ["10", "11", "12"]:
        return month_number
    else:
        return "0" + str(month_number)


def create_recurrent_invoices(invoices):
    today = datetime.today()
    month = get_right_month_format(today.month)
    for invoice in invoices:
        max_invoice_number = get_max_invoice_number()
        payment_date = today + timedelta(
            days=(invoice.payment_date - invoice.sale_date).days
        )

        new_invoice = Invoice.objects.create(
            invoice_number=f"{max_invoice_number}/{month}/{today.year}",
            invoice_type=Invoice.INVOICE_SALES,
            company=invoice.company,
            client=invoice.client,
            person=invoice.person,
            create_date=today,
            sale_date=today,
            payment_date=payment_date,
            payment_method=invoice.payment_method,
            currency=invoice.currency,
            account_number=invoice.account_number,
            is_recurring=False,
            is_last_day=invoice.is_last_day,
            is_paid=False,
            is_settled=False,
        )

        for item in invoice.items.all():
            item.pk = None
            item.invoice = new_invoice
            item.save()

        subject = _("New recurring invoice %(nr)s") % {"nr": new_invoice.invoice_number}
        content = _(
            "A new recurring invoice has been created\n"
            "Best regards,\n"
            "Invoice Factory"
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
    summary_date = today - timedelta(days=today.day)

    companies = Company.objects.filter(is_my_company=True)

    for company in companies:
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
            "Invoice Factory"
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
