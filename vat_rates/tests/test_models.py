import pytest

from vat_rates.factories import VatRateFactory


@pytest.mark.django_db
class TestVatRateModel:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.vat_rate = VatRateFactory.create()

    def test_returns_str(self):
        assert self.vat_rate.__str__() == str(self.vat_rate.rate)
