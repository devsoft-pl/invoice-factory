import datetime

import pytest

from currencies.factories import CurrencyFactory, ExchangeRateFactory


@pytest.mark.django_db
class TestCurrencyModel:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.currency = CurrencyFactory.create()

    def test_returns_str_currency_code(self):
        assert self.currency.__str__() == self.currency.code

    def test_returns_only_last_exchange_rate(self):
        exchange_rate = ExchangeRateFactory.create(
            currency=self.currency, date=datetime.datetime(2023, 8, 5)
        )
        last_exchange_rate = ExchangeRateFactory.create(
            currency=self.currency, date=datetime.datetime(2023, 8, 10)
        )

        assert self.currency.last_exchange_rate == last_exchange_rate
        assert self.currency.last_exchange_rate != exchange_rate


@pytest.mark.django_db
class TestExchangeRateModel:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.exchange_rate = ExchangeRateFactory.create()

    def test_returns_str_currency_code_with_date(self):
        assert (
            self.exchange_rate.__str__()
            == f"{self.exchange_rate.currency.code}: {self.exchange_rate.date}"
        )
