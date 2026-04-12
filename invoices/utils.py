import calendar
import copy
import logging
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from dateutil.relativedelta import relativedelta
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from xhtml2pdf import pisa

from invoices.models import Invoice

logger = logging.getLogger(__name__)

FIRST_INVOICE_NUMBER = 1


def clone(instance):
    cloned = copy.copy(instance)
    cloned.pk = None
    try:
        delattr(cloned, "_prefetched_objects_cache")
    except AttributeError:
        pass
    return cloned


def create_correction_invoice_number(invoice: Invoice):
    invoice_number_parts = invoice.invoice_number.split("/")
    invoice_number_parts.insert(3, "k")
    return "/".join(invoice_number_parts)


def get_invoice_with_max_sale_date(company, person):
    today = datetime.today()
    query_filter = {
        "invoice_type": Invoice.INVOICE_SALES,
        "is_recurring": False,
        "sale_date__year": today.year,
        "sale_date__month": today.month,
    }
    if company:
        query_filter["company"] = company
        query_filter["person__isnull"] = True
    elif person:
        query_filter["person"] = person
        query_filter["company__isnull"] = True
    else:
        return None
    return Invoice.objects.filter(**query_filter).order_by("-sale_date", "-pk").first()


def get_max_invoice_number(company=None, person=None):
    max_sale_date_invoice = get_invoice_with_max_sale_date(company, person)
    current_year = datetime.today().year
    if (
        not max_sale_date_invoice
        or max_sale_date_invoice.sale_date.year != current_year
    ):
        return FIRST_INVOICE_NUMBER
    else:
        last_invoice_number = max_sale_date_invoice.invoice_number.split("/")[0]
        return int(last_invoice_number) + 1


def get_right_month_format(month_number):
    return str(month_number).zfill(2)


def _create_new_invoice_from_template(template_invoice, today):
    month = get_right_month_format(today.month)
    max_invoice_number = get_max_invoice_number(
        template_invoice.company, template_invoice.person
    )
    payment_date = today + timedelta(
        days=(template_invoice.payment_date - template_invoice.sale_date).days
    )
    return Invoice.objects.create(
        invoice_number=f"{max_invoice_number}/{month}/{today.year}",
        invoice_type=Invoice.INVOICE_SALES,
        company=template_invoice.company,
        client=template_invoice.client,
        person=template_invoice.person,
        create_date=today,
        sale_date=today,
        payment_date=payment_date,
        payment_method=template_invoice.payment_method,
        currency=template_invoice.currency,
        account_number=template_invoice.account_number,
        is_recurring=False,
        is_last_day=template_invoice.is_last_day,
        is_paid=False,
        is_settled=False,
    )


def _copy_items_to_new_invoice(template_invoice, new_invoice):
    for item in template_invoice.items.all():
        item.pk = None
        item.invoice = new_invoice
        item.save()


def _send_success_notification(new_invoice):
    subject = _("New recurring invoice %(nr)s") % {"nr": new_invoice.invoice_number}
    content = _(
        "A new recurring invoice has been created\n" "Best regards,\n" "Invoice-Factory"
    )
    html = new_invoice.get_html_for_pdf()

    def link_callback(uri, rel):
        return str(Path(rel) / "invoices" / uri.lstrip("/"))

    with tempfile.NamedTemporaryFile(suffix=".pdf") as invoice_file:
        pisa.CreatePDF(html, dest=invoice_file, link_callback=link_callback)
        invoice_file.seek(0)
        files = [
            {
                "name": f"{new_invoice.invoice_number.replace('/', '-')}.pdf",
                "content": invoice_file.read(),
            }
        ]
        user = new_invoice.get_user()
        if user:
            user.send_email(subject, content, files)


def _reschedule_template_for_next_month(template_invoice):
    if template_invoice.is_last_day:
        next_month_date = template_invoice.sale_date + relativedelta(months=1)
        _, last_day = calendar.monthrange(next_month_date.year, next_month_date.month)
        template_invoice.sale_date = next_month_date.replace(day=last_day)
    else:
        template_invoice.sale_date += relativedelta(months=1)
    template_invoice.save(update_fields=["sale_date"])


def _handle_recurring_invoice_failure(template_invoice, error):
    logger.error(
        f"Failed to create recurring invoice from template #{template_invoice.pk}. Error: {error}",
        exc_info=True,
    )
    user = template_invoice.get_user()
    if user:
        subject = _("Failed to create recurring invoice")
        content = _(
            "Dear User,\n\n"
            "We tried to automatically create a recurring invoice based on template "
            "from %(date)s, but an error occurred.\n\n"
            "Please log in to the application and create this invoice manually.\n\n"
            "Best regards,\n"
            "Invoice-Factory"
        ) % {"date": template_invoice.sale_date.strftime("%Y-%m-%d")}
        user.send_email(subject, content)


def create_recurrent_invoices(invoices):
    today = datetime.today()

    for invoice_template in invoices:
        try:
            with transaction.atomic():
                invoice_to_process = (
                    Invoice.objects.select_for_update()
                    .filter(pk=invoice_template.pk)
                    .first()
                )

                if not invoice_to_process:
                    continue

                if invoice_to_process.sale_date != invoice_template.sale_date:
                    continue

                new_invoice = _create_new_invoice_from_template(
                    invoice_to_process, today
                )
                _copy_items_to_new_invoice(invoice_to_process, new_invoice)
                _reschedule_template_for_next_month(invoice_to_process)

            _send_success_notification(new_invoice)
        except Exception as e:
            _handle_recurring_invoice_failure(invoice_template, e)
