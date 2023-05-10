import pytest
from vat_rates.models import VatRate

@pytest.mark.django_db
class TestVatRateModel:

    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.vat_rate = VatRate.objects.create(rate="23")

    def test_str_returns_vat_rate(self):
        assert self.vat_rate.__str__() == self.vat_rate.rate
