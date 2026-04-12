from decimal import Decimal

import pytest

from invoices.factories import InvoiceSellFactory
from items.factories import ItemFactory
from vat_rates.factories import VatRateFactory


@pytest.mark.django_db
class TestItemModel:
    @pytest.fixture(autouse=True)
    def set_up(self):
        vat = VatRateFactory.create(rate=23)
        self.item = ItemFactory.create(amount=2, net_price=1200, vat=vat)

    def test_returns_str_item_name(self):
        assert self.item.__str__() == self.item.name

    def test_return_net_amount(self):
        assert self.item.net_amount == Decimal("2400")

    def test_returns_tax_amount(self):
        assert self.item.tax_amount == Decimal("552")

    def test_tax_amount_when_vat_is_none(self):
        item = ItemFactory.create(amount=2, net_price=Decimal("1200.00"), vat=None)

        assert item.tax_amount == Decimal("0.00")

    def test_returns_gross_amount(self):
        assert self.item.gross_amount == Decimal("2952")

    def test_gross_amount_when_vat_is_none(self):
        item = ItemFactory.create(amount=2, net_price=Decimal("1200.00"), vat=None)

        assert item.gross_amount == Decimal("2400.00")

    def test_invoice_totals_are_updated_after_item_save(self):
        invoice = InvoiceSellFactory.create(
            net_amount=Decimal("0.00"), gross_amount=Decimal("0.00")
        )
        vat = VatRateFactory.create(rate=23)
        item = ItemFactory.create(
            invoice=invoice, amount=1, net_price=Decimal("100.00"), vat=vat
        )

        invoice.refresh_from_db()
        assert invoice.net_amount == Decimal("0.00")
        assert invoice.gross_amount == Decimal("0.00")

        invoice.update_totals()
        invoice.refresh_from_db()

        expected_net = item.net_amount
        expected_gross = item.gross_amount

        assert invoice.net_amount == expected_net
        assert invoice.gross_amount == expected_gross

    def test_invoice_totals_are_updated_after_item_delete(self):
        invoice = InvoiceSellFactory.create(
            net_amount=Decimal("0.00"), gross_amount=Decimal("0.00")
        )
        vat = VatRateFactory.create(rate=23)
        item1 = ItemFactory.create(
            invoice=invoice, amount=1, net_price=Decimal("100.00"), vat=vat
        )
        ItemFactory.create(
            invoice=invoice, amount=2, net_price=Decimal("50.00"), vat=vat
        )

        invoice.update_totals()
        invoice.refresh_from_db()

        assert invoice.net_amount == Decimal("200.00")
        assert invoice.gross_amount == Decimal("246.00")

        item1.delete()
        invoice.update_totals()
        invoice.refresh_from_db()

        assert invoice.net_amount == Decimal("100.00")
        assert invoice.gross_amount == Decimal("123.00")
