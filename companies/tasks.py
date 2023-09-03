import logging

from celery.exceptions import Ignore
from django.conf import settings
from django.core.mail import send_mail
from django.utils.translation import gettext as _

from base.celery import app
from companies.govs_adapters.ceidg_adapter import CEIDGAdapter
from companies.models import Company

logger = logging.getLogger(__name__)


@app.task(name="check_company_status_for_all_contractors")
def check_company_status_for_all_contractors():
    logger.info("Trying to check company status for all contractors")

    companies = Company.objects.filter(is_my_company=False)

    for company in companies:
        check_company_status.apply_async(args=[company.id])


@app.task(name="check_company_status")
def check_company_status(instance_id):
    logger.info("Trying to check company status for contractor")

    adapter = CEIDGAdapter(settings.CEIDG_API_TOKEN)

    try:
        company = Company.objects.get(pk=instance_id)
    except Company.DoesNotExist:
        raise Ignore()

    logger.info(
        f"Trying to check contractor company status for NIP: {company.nip} and user {company.user}"
    )

    is_active = adapter.is_company_active(company.nip)

    if not is_active:
        if company.user.email:
            subject = _("Contractor's company status")
            content = _(
                "The company status of the contractor with the NIP: %(company_nip)s number in CEIDG is not active.\n"
                " Check the contractor's details again\n"
                "Best regards,\n"
                "Invoice Manager"
            ) % {"company_nip": company.nip}
            send_mail(
                subject,
                content,
                from_email=settings.EMAIL_SENDER,
                recipient_list=[company.user.email],
            )
