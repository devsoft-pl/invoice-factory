import pytest

from invoices.factories import InvoiceFactory
from items.factories import ItemFactory


@pytest.mark.django_db
class TestInvoiceModel:
    @pytest.fixture(autouse=True)
    def set_up(self):
        self.invoice = InvoiceFactory.create()
        self.item = ItemFactory.create(invoice=self.invoice)
        self.item_2 = ItemFactory.create(invoice=self.invoice)

    def test_str_returns_item_name(self):
        assert self.invoice.__str__() == self.invoice.invoice_number

    def test_returns_net_sum(self):
        net_amount_1 = self.item.amount * self.item.net_price
        nut_amount_2 = self.item_2.amount * self.item_2.net_price
        assert self.invoice.net_amount == net_amount_1 + nut_amount_2
