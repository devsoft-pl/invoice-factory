from decimal import Decimal

import pytest

from invoices.factories import InvoiceFactory
from items.factories import ItemFactory


@pytest.mark.django_db
class TestInvoiceModel:
    @pytest.fixture(autouse=True)
    def set_up(self):
        self.invoice = InvoiceFactory.create()
        self.invoice_2 = InvoiceFactory.create()
        self.item = ItemFactory.create(invoice=self.invoice)
        self.item_2 = ItemFactory.create(invoice=self.invoice)

    def test_str_returns_item_name(self):
        assert self.invoice.__str__() == self.invoice.invoice_number

    def test_returns_net_sum(self):
        net_amount_1 = self.item.amount * self.item.net_price
        nut_amount_2 = self.item_2.amount * self.item_2.net_price
        assert self.invoice.net_amount == net_amount_1 + nut_amount_2

    def test_returns_zero_net_sum_if_no_items(self):
        assert self.invoice_2.net_amount == Decimal("0")

    def test_returns_tax_amount_sum(self):
        tax_amount_1 = (self.item.net_amount * self.item.vat.rate) / 100
        tax_amount_2 = (self.item_2.net_amount * self.item_2.vat.rate) / 100
        assert self.invoice.tax_amount == tax_amount_1 + tax_amount_2

    def test_returns_zero_tax_amount_if_no_items(self):
        assert self.invoice_2.tax_amount == Decimal("0")

    def test_returns_gross_amount_sum(self):
        gross_amount_1 = Decimal(self.item.net_amount + self.item.tax_amount)
        gross_amount_2 = Decimal(self.item_2.net_amount + self.item_2.tax_amount)
        assert self.invoice.gross_amount == gross_amount_1 + gross_amount_2

    def test_returns_zero_gross_amount_if_no_items(self):
        assert self.invoice_2.gross_amount == Decimal("0")

    def test_returns_name_item(self):
        assert self.invoice.name_item == self.item.name

    def test_returns_pkwiu_item(self):
        assert self.invoice.pkwiu_item == self.item.pkwiu

    def test_returns_amount_item(self):
        assert self.invoice.amount_item == self.item.amount

    def test_returns_vat_item(self):
        assert self.invoice.vat_item == self.item.vat

    def test_returns_price_item(self):
        assert self.invoice.price_item() == self.item.net_price
