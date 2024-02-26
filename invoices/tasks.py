import calendar
import logging
import tempfile
from datetime import datetime, timedelta, date

from django.utils.translation import gettext as _
from xhtml2pdf import pisa

from base.celery import app
from companies.models import Company
from invoices.models import Invoice
from summary_recipients.models import SummaryRecipient

logger = logging.getLogger(__name__)

"""
1. TAK Pobrać dzisiejszy dzień  --> 26.02.2024 
2. TAK Pobrać dzień z dziś --> 26
3. TAK Pobrać rok z dziś  --> 2024
4. TAK/NIE Sprawdzić, czy dziś jest ostatni dzień miesiąca
5. TAK Sprawdzić, czy dziś jest ostatni miesiąc roku
6. TAK Stworzyć pierwszy miesiąc w roku
7. TAK Pobrać faktury, które mają is_recurring=True
8. TAK Wydiągnać te faktury, gdzie dzień w sale_data == dniu dziejszemu
9. TAK Jeśli nie ma to nie ma tworzenia cykliczności
10. TAK Jeśli jest tak to:
10a. TAK Pobieram ostatnią fakturę sprzedażową dla firmy i persona
10b. TAK Pobieram numer tej faktury
10c. TAK Wyciągam fakturę i najwięszym numerem
10d. TAK Tworze nową fakturę powiększoną o 1 od tej najnowejszej faktury sprzedażowej
"""

LAST_MONTH_OF_YEAR = 12


def is_last_day_of_month():
    today = datetime.today()
    last_day_of_month = calendar.monthrange(today.year, today.month)[1]

    return today.day == last_day_of_month


def first_month_of_year():
    today = datetime.today()
    first_day_of_year = date(today.year, 1, 1)

    return first_day_of_year.month


def next_month_first_day():
    today = datetime.today()

    last_day_of_month = calendar.monthrange(today.year, today.month)[1]
    next_month_first_day = date(today.year, today.month, last_day_of_month) + timedelta(days=1)

    return next_month_first_day


def get_max_number(data_numbers):
    numbers = [int(number) for number in data_numbers]
    max_number = max(numbers)
    return max_number


@app.task(name="create_invoices_for_recurring")
def create_invoices_for_recurring2():
    today = datetime.today()

    invoices = Invoice.objects.filter(is_recurring=True)
    invoices_with_current_day = [invoice for invoice in invoices if invoice.sale_date.day == today.day]

    next_date = next_month_first_day()
    future_invoices_created = Invoice.objects.filter(invoice_type=Invoice.INVOICE_SALES, sale_date__gt=next_date)

    future_invoices_number = [future_invoice.invoice_number for future_invoice in future_invoices_created]

    first_element_invoice_numbers = [invoice.split('/')[0] for invoice in future_invoices_number]
    max_number = get_max_number(first_element_invoice_numbers)

    if today.month == LAST_MONTH_OF_YEAR:
        for invoice in invoices_with_current_day:
            payment_date = today + timedelta(
                days=(invoice.payment_date - invoice.sale_date).days
            )
            Invoice.objects.create(
                invoice_number=f"{max_number + 1}/{today.year + 1}",
                invoice_type=Invoice.INVOICE_SALES,
                company=invoice.company,
                is_recurring=False,
                is_settled=False,
                create_date=today,   # data plus miesiąc
                sale_date=today,     # data plus miesiąc
                payment_date=payment_date,
                payment_method=invoice.payment_method,
                currency=invoice.currency,
                account_number=invoice.account_number,
                client=invoice.client,
                person=invoice.person,
                settlement_date=None,
                is_paid=False,
            )
    else:
        for invoice in invoices_with_current_day:
            payment_date = today + timedelta(
                days=(invoice.payment_date - invoice.sale_date).days
            )
            Invoice.objects.create(
                invoice_number=f"{max_number + 1}/{today.year}",
                invoice_type=Invoice.INVOICE_SALES,
                company=invoice.company,
                is_recurring=False,
                is_settled=False,
                create_date=today,
                sale_date=today,
                payment_date=payment_date,
                payment_method=invoice.payment_method,
                currency=invoice.currency,
                account_number=invoice.account_number,
                client=invoice.client,
                person=invoice.person,
                settlement_date=None,
                is_paid=False,
            )



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
            is_paid=False,
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
