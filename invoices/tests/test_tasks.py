import datetime
from unittest.mock import patch

import pytest

from companies.factories import CompanyFactory
from currencies.factories import CurrencyFactory
from invoices.factories import InvoiceSellFactory, InvoiceSellPersonFactory
from invoices.models import Invoice
from invoices.tasks import (
    create_invoices_for_recurring,
    send_monthly_summary_to_recipients,
)
from invoices.utils import get_right_month_format
from items.factories import ItemFactory
from summary_recipients.factories import SummaryRecipientFactory
from summary_recipients.models import SummaryRecipient


@pytest.mark.django_db
class TestRecurrentInvoiceTasks:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.currency = CurrencyFactory.create(code="PLN")
        self.company = CompanyFactory.create(is_my_company=True)
        self.client = CompanyFactory.create(is_my_company=False)

    @patch("invoices.tasks.datetime")
    @patch("invoices.utils.datetime")
    def test_returns_first_invoice_number_when_is_first_in_new_year(
        self, datetime_mock, datetime_2_mock
    ):
        datetime_mock.today.return_value = datetime.date(2024, 1, 31)
        datetime_2_mock.today.return_value = datetime.date(2024, 1, 31)
        InvoiceSellFactory.create(
            is_recurring=True,
            currency=self.currency,
            sale_date=datetime_mock.today.return_value,
            is_last_day=True,
            company=self.company,
            client=self.client,
        )
        InvoiceSellFactory.create(
            invoice_number="1/12/2023",
            is_recurring=False,
            currency=self.currency,
            sale_date=datetime.date(2023, 12, 31),
            is_last_day=True,
            company=self.company,
            client=self.client,
        )

        create_invoices_for_recurring()

        invoices = Invoice.objects.filter(is_recurring=False, sale_date__year=2024)
        assert invoices.count() == 1
        assert invoices.first().invoice_number == "1/01/2024"
        assert Invoice.objects.count() == 3

    @patch("invoices.tasks.datetime")
    @patch("invoices.utils.datetime")
    def test_returns_second_invoice_number_when_is_second_in_new_year(
        self, datetime_mock, datetime_2_mock
    ):
        datetime_mock.today.return_value = datetime.date(2024, 1, 31)
        datetime_2_mock.today.return_value = datetime.date(2024, 1, 31)
        InvoiceSellFactory.create(
            invoice_number="1/01/2024",
            is_recurring=False,
            currency=self.currency,
            sale_date=datetime.date(2024, 1, 25),
            company=self.company,
            client=self.client,
        )
        InvoiceSellFactory.create(
            is_recurring=True,
            currency=self.currency,
            sale_date=datetime_mock.today.return_value,
            is_last_day=True,
            company=self.company,
            client=self.client,
        )

        create_invoices_for_recurring()

        invoices = Invoice.objects.filter(is_recurring=False, sale_date__year=2024)
        assert invoices.count() == 2

        invoice = (
            Invoice.objects.filter(
                invoice_type=Invoice.INVOICE_SALES, is_recurring=False
            )
            .order_by("-sale_date", "pk")
            .first()
        )

        assert invoice.invoice_number == "2/01/2024"
        assert Invoice.objects.count() == 3

    @patch("invoices.tasks.datetime")
    @pytest.mark.parametrize(
        "current_date, last_day",
        [
            (datetime.date(2023, 8, 31), True),
            (datetime.date(2023, 8, 25), False),
        ],
    )
    def test_creates_new_invoice_if_recurring_invoice_is_set_for_different_days(
        self, datetime_mock, current_date, last_day
    ):
        datetime_mock.today.return_value = current_date
        invoice = InvoiceSellFactory.create(
            is_recurring=True,
            currency=self.currency,
            sale_date=current_date,
            is_last_day=last_day,
            company=self.company,
            client=self.client,
        )
        ItemFactory.create_batch(2, invoice=invoice)

        create_invoices_for_recurring()

        assert Invoice.objects.count() == 2
        assert (
            invoice.items.count()
            == Invoice.objects.get(is_recurring=False).items.count()
        )

    @patch("invoices.tasks.datetime")
    @pytest.mark.parametrize(
        "current_date, last_day",
        [
            (datetime.date(2023, 8, 31), True),
            (datetime.date(2023, 8, 25), False),
        ],
    )
    def test_creates_new_person_invoice_if_recurring_invoice_is_set_for_different_days(
        self, datetime_mock, current_date, last_day
    ):
        datetime_mock.today.return_value = current_date
        invoice = InvoiceSellPersonFactory.create(
            is_recurring=True,
            currency=self.currency,
            sale_date=current_date,
            is_last_day=last_day,
            company=self.company,
            client=self.client,
        )
        ItemFactory.create_batch(2, invoice=invoice)

        create_invoices_for_recurring()

        assert Invoice.objects.count() == 2
        assert (
            invoice.items.count()
            == Invoice.objects.get(is_recurring=False).items.count()
        )

    @patch("invoices.tasks.datetime")
    def test_not_creates_new_invoice_if_recurring_is_false(self, datetime_mock):
        InvoiceSellFactory.create(is_recurring=False, currency=self.currency)
        datetime_mock.today.return_value = datetime.date(2023, 8, 15)

        create_invoices_for_recurring()

        assert Invoice.objects.count() == 1

    @pytest.mark.parametrize("month, expected", [[10, 10], [1, "01"]])
    def test_returns_right_month_format(self, month, expected):
        right_month = get_right_month_format(month)

        assert right_month == expected

    @patch("invoices.tasks.datetime")
    @patch("invoices.utils.datetime")
    def test_returns_correct_invoice_number_when_month_is_october(
        self, datetime_mock, datetime_2_mock
    ):
        datetime_mock.today.return_value = datetime.date(2024, 10, 27)
        datetime_2_mock.today.return_value = datetime.date(2024, 10, 27)
        InvoiceSellFactory.create(
            is_recurring=True,
            currency=self.currency,
            sale_date=datetime_mock.today.return_value,
            is_last_day=False,
            company=self.company,
            client=self.client,
        )

        create_invoices_for_recurring()

        invoices = Invoice.objects.filter(is_recurring=False, sale_date__year=2024)
        assert invoices.count() == 1
        assert Invoice.objects.count() == 2
        assert invoices.first().invoice_number == "1/10/2024"


@pytest.mark.django_db
class TestSummaryRecipientTasks:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.today = datetime.datetime.today()
        self.last_month_date = self.today - datetime.timedelta(days=self.today.day)
        self.last_month_date_2 = self.last_month_date.replace(day=7)
        self.company = CompanyFactory.create(is_my_company=True)
        self.currency = CurrencyFactory.create(code="PLN")
        self.invoice_1 = InvoiceSellFactory.create(
            company=self.company,
            create_date=self.last_month_date,
            is_settled=False,
            currency=self.currency,
            is_recurring=False,
        )
        self.invoice_2 = InvoiceSellFactory.create(
            company=self.company,
            create_date=self.last_month_date_2,
            currency=self.currency,
            is_recurring=False,
        )

    @patch("summary_recipients.models.SummaryRecipient.send_email")
    def test_send_monthly_summary_in_defined_day(self, send_email_mock):
        SummaryRecipientFactory.create(company=self.company, day=self.today.day)

        send_monthly_summary_to_recipients()

        send_email_mock.assert_called()
        files = send_email_mock.call_args[0][2]
        assert len(files) == 2

    @patch("summary_recipients.models.SummaryRecipient.send_email")
    def test_not_send_monthly_summary_if_another_day_other_than_defined_day(
        self, send_email_mock
    ):
        assert not SummaryRecipient.objects.exists()

        SummaryRecipientFactory.create(company=self.company)

        send_monthly_summary_to_recipients()

        send_email_mock.assert_not_called()

    @pytest.mark.parametrize(
        "final_call, expected_value", [[True, True], [False, False]]
    )
    @patch("summary_recipients.models.SummaryRecipient.send_email")
    def test_if_invoice_is_settled_on_final_call(
        self, send_email_mock, final_call, expected_value
    ):
        SummaryRecipientFactory.create(
            company=self.company, day=self.today.day, final_call=final_call
        )

        send_monthly_summary_to_recipients()
        self.invoice_1.refresh_from_db()

        assert self.invoice_1.is_settled is expected_value
        send_email_mock.assert_called_once()

    @patch("summary_recipients.models.SummaryRecipient.send_email")
    def test_send_monthly_summary_on_last_day_of_month(self, send_email_mock):
        today = datetime.datetime(year=2024, month=10, day=31)
        last_month_date = datetime.datetime(year=2024, month=9, day=15)

        invoice = InvoiceSellFactory.create(
            company=self.company,
            create_date=last_month_date,
            is_settled=False,
            currency=self.currency,
            is_recurring=False,
        )

        SummaryRecipientFactory.create(
            company=self.company, is_last_day=True, day=31, final_call=True
        )

        with patch("invoices.tasks.datetime") as datetime_mock:
            datetime_mock.today.return_value = today
            send_monthly_summary_to_recipients()
        invoice.refresh_from_db()

        assert invoice.is_settled is True
        send_email_mock.assert_called_once()
