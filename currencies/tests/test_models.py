import pytest

from currencies.factories import CurrencyFactory


@pytest.mark.django_db
class TestCurrencyModel:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.currency = CurrencyFactory.create()

    def test_str_returns_currency_code(self):
        assert self.currency.__str__() == self.currency.code
