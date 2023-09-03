from datetime import datetime
from unittest.mock import call, patch

import pytest

from currencies.factories import CurrencyFactory
from currencies.models import ExchangeRate
from currencies.tasks import (get_exchange_rate_for_currency,
                              get_exchange_rates_for_all)
from users.factories import UserFactory


@pytest.mark.django_db
class TestExchangeRatesTasks:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.user = UserFactory.create()
        self.currency_usd = CurrencyFactory.create(user=self.user, code="USD")

    @patch("currencies.tasks.get_exchange_rate_for_currency.apply_async")
    def test_should_create_exchange_rates_when_buy_rate_and_sell_rate(
        self, get_exchange_rate_for_currency_mock
    ):
        self.currency_eur = CurrencyFactory.create(user=self.user, code="eur")

        get_exchange_rates_for_all()

        assert get_exchange_rate_for_currency_mock.call_count == 2

    @pytest.mark.parametrize(
        "buy_rate, sell_rate, expected_count",
        [["3.9758", "4.0562", 1], [None, None, 0]],
    )
    @patch("currencies.nbp_adapter.NBPExchangeRatesAdapter.get_currency_buy_rate")
    @patch("currencies.nbp_adapter.NBPExchangeRatesAdapter.get_currency_sell_rate")
    def test_should_returns_expected_rates(
        self,
        get_currency_buy_rate_mock,
        get_currency_sell_rate_mock,
        buy_rate,
        sell_rate,
        expected_count,
    ):
        get_currency_buy_rate_mock.return_value = buy_rate
        get_currency_sell_rate_mock.return_value = sell_rate

        get_exchange_rate_for_currency(self.currency_usd.id)

        assert get_currency_buy_rate_mock.call_args_list == [call("usd")]
        assert (
            ExchangeRate.objects.filter(
                date=datetime.today(), currency=self.currency_usd
            ).count()
            == expected_count
        )
