import calendar
import logging
import tempfile
from datetime import datetime, timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from xhtml2pdf import pisa

from base.celery import app
from companies.models import Company
from currencies.models import Currency
from invoices.adapters.ksef_adapter import KSeFAdapter
from invoices.adapters.ksef_mapper import (
    map_ksef_invoice_to_dict,
    map_ksef_invoice_to_items,
)
from invoices.forms import is_last_day_of_month
from invoices.models import Invoice
from invoices.utils import create_recurrent_invoices
from items.models import Item
from summary_recipients.models import SummaryRecipient
from vat_rates.models import VatRate

logger = logging.getLogger(__name__)

DEFAULT_CURRENCY_CODE = "PLN"


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

        if not invoices.exists():
            continue

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
            invoices.update(is_settled=True)


@app.task(name="fetch_purchase_invoices_from_ksef")
def fetch_purchase_invoices_from_ksef():
    today = timezone.now().date()
    companies = Company.objects.filter(
        is_my_company=True, ksef_token__isnull=False
    ).exclude(ksef_token="")

    for company in companies:
        new_invoices_count = _fetch_invoices_for_company(company, today)

        if new_invoices_count > 0:
            _send_ksef_notification_email(company.user, company, new_invoices_count)


def _fetch_invoices_for_company(company: Company, today) -> int:
    new_invoices_count = 0

    with KSeFAdapter(company.ksef_token, company.nip) as adapter:
        if not adapter.authenticate():
            logger.error("KSeF authentication failed for %s", company.name)
            return 0

        if company.ksef_last_fetched_at:
            current_day = company.ksef_last_fetched_at.date()
        else:
            current_day = company.created_at.date()

        while current_day <= today:
            total_processed = 0
            fetch_successful = False

            try:
                for page in adapter.get_all_purchase_invoices(current_day, current_day):
                    with transaction.atomic():
                        for ksef_invoice in page:
                            is_created = _save_ksef_invoice(
                                ksef_invoice, company, adapter
                            )
                            if is_created:
                                new_invoices_count += 1
                            total_processed += 1
                fetch_successful = True
            except Exception as e:
                logger.error(
                    "Failed to fetch or save KSeF invoices for %s on %s: %s",
                    company.name,
                    current_day,
                    e,
                )

            if fetch_successful:
                logger.info(
                    "Processed %d KSeF invoices for %s on %s",
                    total_processed,
                    company.name,
                    current_day,
                )
                end_of_day = datetime.combine(current_day, datetime.max.time())
                company.ksef_last_fetched_at = timezone.make_aware(end_of_day)
                company.save(update_fields=["ksef_last_fetched_at"])

                current_day += timedelta(days=1)
            else:
                break

    return new_invoices_count


def _send_ksef_notification_email(user, company, new_invoices_count):
    subject = _("New purchase invoices from KSeF")
    message = _(
        "Hello,\n\n"
        "We have automatically downloaded %(count)d new purchase invoice(s) from KSeF for your company %(company)s.\n"
        "Please log in to the application to review them.\n\n"
        "Best regards,\n"
        "Invoice-Factory"
    ) % {"count": new_invoices_count, "company": company.name}

    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_SENDER,
            [user.email],
            fail_silently=True,
        )
        logger.info(
            "Sent KSeF notification email to %s (invoices: %d)",
            user.email,
            new_invoices_count,
        )
    except Exception as e:
        logger.error("Failed to send KSeF notification to %s: %s", user.email, e)


def _save_ksef_invoice(ksef_invoice: dict, company, adapter) -> bool:
    invoice_number = ksef_invoice.get("invoiceNumber")

    if Invoice.objects.filter(invoice_number=invoice_number, company=company).exists():
        logger.debug("KSeF invoice %s already exists, skipping", invoice_number)
        return False

    xml = adapter.get_invoice_xml(ksef_invoice["ksefNumber"])
    if xml is None:
        raise Exception(
            f"Failed to fetch XML for KSeF invoice {ksef_invoice['ksefNumber']}"
        )

    invoice_dict = map_ksef_invoice_to_dict(ksef_invoice, company, xml)
    items_data = map_ksef_invoice_to_items(xml)

    currency_code = ksef_invoice.get("currency", DEFAULT_CURRENCY_CODE)
    currency, _ = Currency.objects.get_or_create(code=currency_code, user=company.user)
    invoice_dict["currency"] = currency

    user = company.user
    vat_rate_cache = {}

    invoice = Invoice.objects.create(**invoice_dict)

    for item_data in items_data:
        rate = item_data["vat_rate"]
        if rate not in vat_rate_cache:
            vat_rate, _ = VatRate.objects.get_or_create(rate=rate, user=user)
            vat_rate_cache[rate] = vat_rate
        else:
            vat_rate = vat_rate_cache[rate]

        Item.objects.create(
            invoice=invoice,
            name=item_data["name"],
            amount=item_data["amount"],
            net_price=item_data["net_price"],
            vat=vat_rate,
        )

    invoice.update_totals()

    logger.info("Saved KSeF invoice %s for %s", invoice_number, company.name)
    return True
