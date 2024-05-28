import logging

from celery.exceptions import Ignore
from django.conf import settings
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
        f"Trying to check contractor company status for NIP: "
        f"{company.nip} and user {company.user}"
    )

    is_active = adapter.is_company_active(company.nip)

    if not is_active:
        subject = _("Contractor's company status")
        content = _(
            "The company status of the contractor with the NIP: "
            "%(company_nip)s number in CEIDG is not active.\n"
            " Check the contractor's details again\n"
            "Best regards,\n"
            "Invoice Factory"
        ) % {"company_nip": company.nip}

        company.user.send_email(subject, content)
