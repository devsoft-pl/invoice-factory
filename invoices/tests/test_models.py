import pytest

from invoices.factories import InvoiceFactory


@pytest.mark.django_db
class TestInvoiceModel:
    @pytest.fixture(autouse=True)
    def set_up(self):
        self.invoice = InvoiceFactory.create()

    def test_str_returns_item_name(self):
        assert self.invoice.__str__() == self.invoice.invoice_number
