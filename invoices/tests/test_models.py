from decimal import Decimal

import pytest

from currencies.factories import ExchangeRateFactory
from invoices.factories import (CorrectionInvoiceRelationFactory,
                                InvoiceSellFactory, YearFactory)
from items.factories import ItemFactory
from vat_rates.factories import VatRateFactory


@pytest.mark.django_db
class TestInvoiceModel:
    @pytest.fixture(autouse=True)
    def set_up(self):
        self.invoice = InvoiceSellFactory.create()
        self.invoice_2 = InvoiceSellFactory.create()
        vat = VatRateFactory.create(rate=23)
        self.item = ItemFactory.create(
            invoice=self.invoice, amount=2, net_price=1200, vat=vat
        )
        self.item_2 = ItemFactory.create(
            invoice=self.invoice, amount=1, net_price=800, vat=vat
        )

    def test_returns_str_item_name(self):
        assert self.invoice.__str__() == self.invoice.invoice_number

    def test_returns_recurring_invoice_name(self):
        self.invoice = InvoiceSellFactory.create(invoice_number="")
        assert self.invoice.__str__() == 'Cykliczna faktura'

    def test_returns_calculated_net_amount(self):
        assert self.invoice.calculate_net_amount() == Decimal("3200")

    def test_returns_zero_calculated_net_amount_if_no_items(self):
        assert self.invoice_2.calculate_net_amount() == Decimal("0")

    def test_returns_tax_amount(self):
        assert self.invoice.tax_amount == Decimal("736")

    def test_returns_zero_tax_amount_if_no_items(self):
        assert self.invoice_2.tax_amount == Decimal("0")

    def test_returns_calculated_gross_amount(self):
        assert self.invoice.calculate_gross_amount() == Decimal("3936")

    def test_returns_zero_calculated_gross_amount_if_no_items(self):
        assert self.invoice_2.calculate_gross_amount() == Decimal("0")

    def test_returns_sell_rate_in_pln(self):
        exchange_rate = ExchangeRateFactory.create(
            currency=self.invoice.currency,
            date=self.invoice.sale_date,
        )

        assert exchange_rate.sell_rate == self.invoice.sell_rate_in_pln

    def test_returns_invoice_sale(self):
        assert self.invoice.is_sell


@pytest.mark.django_db
class TestYearModel:
    @pytest.fixture(autouse=True)
    def set_up(self):
        self.year = YearFactory.create()

    def test_returns_str_for_year(self):
        assert self.year.__str__() == str(self.year.year)


@pytest.mark.django_db
class TestCorrectionInvoiceRelationModel:
    @pytest.fixture(autouse=True)
    def set_up(self):
        self.invoice = InvoiceSellFactory.create(invoice_number="1/2024")
        self.correction_invoice = InvoiceSellFactory.create(invoice_number="1/k/2024")
        self.correction_invoice_relation = CorrectionInvoiceRelationFactory.create(
            invoice=self.invoice, correction_invoice=self.correction_invoice
        )

    def test_returns_str_invoice_number(self):
        assert (
            self.correction_invoice_relation.__str__()
            == f"{self.correction_invoice_relation.invoice.invoice_number}, "
            f"{self.correction_invoice_relation.correction_invoice.invoice_number}"
        )
