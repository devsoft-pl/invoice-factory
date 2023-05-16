from decimal import Decimal

import pytest

from items.factories import ItemFactory
from vat_rates.factories import VatRateFactory


@pytest.mark.django_db
class TestItemModel:
    @pytest.fixture(autouse=True)
    def set_up(self):
        vat = VatRateFactory.create(rate=23)
        self.item = ItemFactory.create(amount=2, net_price=1200, vat=vat)

    def test_str_returns_item_name(self):
        assert self.item.__str__() == self.item.name

    def test_return_net_amount(self):
        assert self.item.net_amount == Decimal("2400")

    def test_returns_tax_amount(self):
        assert self.item.tax_amount == Decimal("552")

    def test_returns_gross_amount(self):
        assert self.item.gross_amount == Decimal("2952")
