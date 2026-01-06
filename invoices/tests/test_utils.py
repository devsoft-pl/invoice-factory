import datetime
from unittest.mock import patch

import pytest

from companies.factories import CompanyFactory
from invoices.factories import InvoiceSellFactory, InvoiceSellPersonToClientFactory
from invoices.utils import (
    clone,
    create_correction_invoice_number,
    get_max_invoice_number,
    get_right_month_format,
)
from persons.factories import PersonFactory
from users.factories import UserFactory


@pytest.mark.django_db
class TestCloneUtil:
    def test_clone_returns_new_instance(self):
        invoice = InvoiceSellFactory.create()
        cloned_invoice = clone(invoice)

        assert cloned_invoice.pk is None
        assert cloned_invoice.invoice_number == invoice.invoice_number
        assert not hasattr(cloned_invoice, "_prefetched_objects_cache")


@pytest.mark.django_db
class TestCreateCorrectionInvoiceNumberUtil:
    def test_create_correction_invoice_number(self):
        invoice = InvoiceSellFactory.create(invoice_number="1/01/2024")
        correction_number = create_correction_invoice_number(invoice)
        assert correction_number == "1/01/2024/k"

    def test_create_correction_invoice_number_with_existing_correction(self):
        invoice = InvoiceSellFactory.create(invoice_number="1/01/2024/k")
        correction_number = create_correction_invoice_number(invoice)
        assert correction_number == "1/01/2024/k/k"


@pytest.mark.django_db
class TestGetMaxInvoiceNumberUtil:
    @patch("invoices.utils.datetime")
    def test_get_max_invoice_number_for_company(self, datetime_mock):
        datetime_mock.today.return_value = datetime.date(2024, 1, 1)
        user = UserFactory()
        company = CompanyFactory.create(user=user)
        InvoiceSellFactory.create(
            company=company,
            invoice_number="1/01/2024",
            sale_date=datetime.date(2024, 1, 1),
            is_recurring=False,
        )
        InvoiceSellFactory.create(
            company=company,
            invoice_number="2/01/2024",
            sale_date=datetime.date(2024, 1, 1),
            is_recurring=False,
        )

        max_number = get_max_invoice_number(company=company)
        assert max_number == 3

    @patch("invoices.utils.datetime")
    def test_get_max_invoice_number_for_person(self, datetime_mock):
        datetime_mock.today.return_value = datetime.date(2024, 1, 1)
        user = UserFactory()
        person = PersonFactory.create(user=user)

        InvoiceSellPersonToClientFactory.create(
            person=person,
            invoice_number="1/01/2024",
            sale_date=datetime.date(2024, 1, 1),
            is_recurring=False,
        )
        InvoiceSellPersonToClientFactory.create(
            person=person,
            invoice_number="2/01/2024",
            sale_date=datetime.date(2024, 1, 1),
            is_recurring=False,
        )

        max_number = get_max_invoice_number(person=person)
        assert max_number == 3

    @patch("invoices.utils.datetime")
    def test_get_max_invoice_number_no_invoices(self, datetime_mock):
        datetime_mock.today.return_value = datetime.date(2024, 1, 1)
        company = CompanyFactory.create()

        max_number = get_max_invoice_number(company=company)
        assert max_number == 1

    @patch("invoices.utils.datetime")
    def test_get_max_invoice_number_no_company_or_person(self, datetime_mock):
        datetime_mock.today.return_value = datetime.date(2024, 1, 1)
        max_number = get_max_invoice_number()

        assert max_number == 1


class TestGetRightMonthFormatUtil:
    def test_get_right_month_format(self):
        assert get_right_month_format(1) == "01"
        assert get_right_month_format(9) == "09"
        assert get_right_month_format(10) == "10"
        assert get_right_month_format(12) == "12"
