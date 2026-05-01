import calendar
import logging
import tempfile
from datetime import datetime, timedelta

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
        with KSeFAdapter(company.ksef_token, company.nip) as adapter:
            if not adapter.authenticate():
                logger.error("KSeF authentication failed for %s", company.name)
                continue

            if company.ksef_last_fetched_at:
                current_day = company.ksef_last_fetched_at.date()
            else:
                current_day = company.created_at.date()

            while current_day <= today:
                total = 0
                fetch_successful = False
                try:
                    for page in adapter.get_all_purchase_invoices(
                        current_day, current_day
                    ):
                        with transaction.atomic():
                            for ksef_invoice in page:
                                _save_ksef_invoice(ksef_invoice, company, adapter)
                                total += 1
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
                        "Saved %d new/checked KSeF invoices for %s on %s",
                        total,
                        company.name,
                        current_day,
                    )
                    end_of_day = datetime.combine(current_day, datetime.max.time())
                    company.ksef_last_fetched_at = timezone.make_aware(end_of_day)
                    company.save(update_fields=["ksef_last_fetched_at"])

                    current_day += timedelta(days=1)
                else:
                    break


def _save_ksef_invoice(ksef_invoice: dict, company, adapter):
    invoice_number = ksef_invoice.get("invoiceNumber")

    if Invoice.objects.filter(invoice_number=invoice_number, company=company).exists():
        logger.debug("KSeF invoice %s already exists, skipping", invoice_number)
        return

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
