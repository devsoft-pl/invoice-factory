import pytest

from currencies.models import Currency


@pytest.mark.django_db
class TestCurrencyModel:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.currency = Currency.objects.create(code="pln")

    def test_str_returns_currency_code(self):
        assert self.currency.__str__() == self.currency.code
