import pytest

from currencies.factories import CurrencyFactory, ExchangeRateFactory


@pytest.mark.django_db
class TestCurrencyModel:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.currency = CurrencyFactory.create()

    def test_str_returns_currency_code(self):
        assert self.currency.__str__() == self.currency.code


@pytest.mark.django_db
class TestExchangeRateModel:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.exchange_rate = ExchangeRateFactory.create()

    def test_str_returns_currency_code_with_date(self):
        assert (
            self.exchange_rate.__str__()
            == f"{self.exchange_rate.currency.code}: {self.exchange_rate.date}"
        )
