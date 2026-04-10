import datetime
from decimal import Decimal
from unittest.mock import ANY, MagicMock, patch

import pytest
from dateutil.relativedelta import relativedelta

from companies.factories import CompanyFactory
from currencies.factories import CurrencyFactory
from invoices.factories import InvoiceSellFactory, InvoiceSellPersonToClientFactory
from invoices.models import Invoice
from invoices.utils import (
    _copy_items_to_new_invoice,
    _create_new_invoice_from_template,
    _handle_recurring_invoice_failure,
    _reschedule_template_for_next_month,
    _send_success_notification,
    clone,
    create_correction_invoice_number,
    create_recurrent_invoices,
    get_max_invoice_number,
    get_right_month_format,
)
from items.factories import ItemFactory
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


@pytest.mark.django_db
class TestRecurringInvoiceHelpers:
    @patch("invoices.utils.get_max_invoice_number", return_value=5)
    def test_create_new_invoice_from_template(self, mock_get_max):
        today = datetime.date(2024, 3, 15)
        template = InvoiceSellFactory.create(is_recurring=True)

        new_invoice = _create_new_invoice_from_template(template, today)

        assert new_invoice.pk is not None
        assert new_invoice.is_recurring is False
        assert new_invoice.invoice_number == "5/03/2024"
        assert new_invoice.company == template.company
        assert new_invoice.client == template.client
        assert new_invoice.sale_date == today

    def test_copy_items_to_new_invoice(self):
        template = InvoiceSellFactory.create()
        ItemFactory.create_batch(3, invoice=template)
        new_invoice = InvoiceSellFactory.create()

        assert new_invoice.items.count() == 0

        _copy_items_to_new_invoice(template, new_invoice)

        assert new_invoice.items.count() == 3
        assert template.items.count() == 3

    @patch("users.models.User.send_email")
    def test_send_success_notification(self, mock_send_email):
        user = UserFactory()
        company = CompanyFactory(user=user)
        pln_currency = CurrencyFactory.create(code="PLN")
        new_invoice = InvoiceSellFactory.create(
            invoice_number="1/2024",
            currency=pln_currency,
            gross_amount=Decimal("123.45"),
            company=company,
        )

        _send_success_notification(new_invoice)

        mock_send_email.assert_any_call(
            "New recurring invoice 1/2024",
            "A new recurring invoice has been created\nBest regards,\nInvoice-Factory",
            ANY,
        )

    @pytest.mark.parametrize(
        "start_date, is_last_day, expected_date",
        [
            (datetime.date(2024, 2, 15), False, datetime.date(2024, 3, 15)),
            (datetime.date(2024, 1, 31), False, datetime.date(2024, 2, 29)),
            (datetime.date(2024, 3, 31), True, datetime.date(2024, 4, 30)),
            (datetime.date(2024, 2, 29), True, datetime.date(2024, 3, 31)),
        ],
    )
    def test_reschedule_template_for_next_month(
        self, start_date, is_last_day, expected_date
    ):
        template = InvoiceSellFactory.create(
            sale_date=start_date, is_last_day=is_last_day
        )

        _reschedule_template_for_next_month(template)

        template.refresh_from_db()
        assert template.sale_date == expected_date

    @patch("invoices.utils.logger.error")
    @patch("users.models.User.send_email")
    def test_handle_recurring_invoice_failure(self, mock_send_email, mock_logger):
        user = UserFactory()
        company = CompanyFactory(user=user)
        pln_currency = CurrencyFactory.create(code="PLN")
        template = InvoiceSellFactory.create(
            sale_date=datetime.date(2024, 1, 1),
            currency=pln_currency,
            company=company,
        )
        error = ValueError("Test error")

        _handle_recurring_invoice_failure(template, error)

        mock_logger.assert_called_once()
        mock_send_email.assert_any_call(
            "Failed to create recurring invoice",
            "Dear User,\n\n"
            "We tried to automatically create a recurring invoice based on template "
            "from 2024-01-01, but an error occurred.\n\n"
            "Please log in to the application and create this invoice manually.\n\n"
            "Best regards,\n"
            "Invoice-Factory",
        )


@pytest.mark.django_db
class TestCreateRecurrentInvoices:
    @patch("invoices.utils._send_success_notification")
    @patch("invoices.utils.get_max_invoice_number", return_value=1)
    @patch("invoices.utils.datetime")
    def test_create_recurrent_invoices_happy_path(
        self, mock_datetime, mock_max_number, mock_send_notification
    ):
        today = datetime.date(2024, 3, 15)
        mock_datetime.today.return_value = today

        template = InvoiceSellFactory.create(
            is_recurring=True, sale_date=today, is_last_day=False
        )
        initial_invoice_count = Invoice.objects.count()

        create_recurrent_invoices([template])

        assert Invoice.objects.count() == initial_invoice_count + 1
        new_invoice = Invoice.objects.get(is_recurring=False)
        assert new_invoice.invoice_number == "1/03/2024"
        mock_send_notification.assert_called_once_with(new_invoice)

        template.refresh_from_db()
        assert template.sale_date == today + relativedelta(months=1)

    @patch("invoices.utils._send_success_notification")
    @patch("invoices.utils._create_new_invoice_from_template")
    @patch("invoices.utils.Invoice.objects.select_for_update")
    @patch("invoices.utils.datetime")
    def test_create_recurrent_invoices_handles_race_condition(
        self,
        mock_datetime,
        mock_select_for_update,
        mock_create_invoice,
        mock_send_notification,
    ):
        today = datetime.date(2024, 3, 15)
        mock_datetime.today.return_value = today

        template = InvoiceSellFactory.create(
            is_recurring=True, sale_date=today, is_last_day=False
        )

        updated_template = clone(template)
        updated_template.sale_date = today + relativedelta(months=1)

        mock_manager = MagicMock()
        mock_manager.filter.return_value.first.return_value = updated_template
        mock_select_for_update.return_value = mock_manager

        initial_invoice_count = Invoice.objects.count()

        create_recurrent_invoices([template])

        assert Invoice.objects.count() == initial_invoice_count
        mock_create_invoice.assert_not_called()
        mock_send_notification.assert_not_called()

    @patch("invoices.utils._send_success_notification")
    @patch("invoices.utils._create_new_invoice_from_template")
    @patch("invoices.utils.Invoice.objects.select_for_update")
    def test_create_recurrent_invoices_skips_deleted_template(
        self, mock_select_for_update, mock_create_invoice, mock_send_notification
    ):
        template = InvoiceSellFactory.build()

        mock_manager = MagicMock()
        mock_manager.filter.return_value.first.return_value = None
        mock_select_for_update.return_value = mock_manager

        initial_invoice_count = Invoice.objects.count()

        create_recurrent_invoices([template])

        assert Invoice.objects.count() == initial_invoice_count
        mock_create_invoice.assert_not_called()
        mock_send_notification.assert_not_called()

    @patch("invoices.utils._handle_recurring_invoice_failure")
    @patch(
        "invoices.utils._create_new_invoice_from_template",
        side_effect=Exception("DB Error"),
    )
    def test_create_recurrent_invoices_handles_exception(
        self, mock_create, mock_handle_failure
    ):
        template = InvoiceSellFactory.create(is_recurring=True)

        create_recurrent_invoices([template])

        mock_create.assert_called_once()
        mock_handle_failure.assert_called_once()
        template.refresh_from_db()
        assert template.is_recurring is True
