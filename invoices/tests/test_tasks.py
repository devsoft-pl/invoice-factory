import datetime
from unittest.mock import patch

import pytest

from invoices.factories import InvoiceFactory
from invoices.models import Invoice
from invoices.tasks import create_invoices_for_recurring
from items.factories import ItemFactory


@pytest.mark.django_db
class TestRecurrentInvoiceTasks:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.invoice = InvoiceFactory.create(is_recurring=True)

    @patch("invoices.tasks.datetime")
    def test_creates_new_invoice_on_last_day_of_month(self, datetime_mock):
        ItemFactory.create_batch(2, invoice=self.invoice)
        datetime_mock.today.return_value = datetime.date(2023, 8, 31)

        create_invoices_for_recurring()

        assert Invoice.objects.count() == 2
        assert (
            self.invoice.items.count()
            == Invoice.objects.get(is_recurring=False).items.count()
        )

    @patch("invoices.tasks.datetime")
    def test_not_creates_new_invoice_if_not_last_day_of_month(self, datetime_mock):
        datetime_mock.today.return_value = datetime.date(2023, 8, 15)

        create_invoices_for_recurring()

        assert Invoice.objects.count() == 1
