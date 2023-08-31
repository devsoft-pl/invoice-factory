from unittest.mock import Mock, patch

import pytest

from currencies.nbp_adapter import NBPExchangeRatesAdapter


class TestNBPExchangeRatesAdapter:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.adapter = NBPExchangeRatesAdapter()
        self.currency_rates_value = {
            "table": "C",
            "currency": "dolar amerykański",
            "code": "USD",
            "rates": [
                {
                    "no": "143/C/NBP/2023",
                    "effectiveDate": "2023-07-26",
                    "bid": 3.9758,
                    "ask": 4.0562,
                }
            ],
        }

    @patch("currencies.nbp_adapter.NBPExchangeRatesAdapter._get_currency_rates")
    def test_get_currency_buy_rate(self, _get_currency_rates_mock):
        _get_currency_rates_mock.return_value = self.currency_rates_value

        assert self.adapter.get_currency_buy_rate("USD") == 3.9758

    @patch("currencies.nbp_adapter.NBPExchangeRatesAdapter._get_currency_rates")
    def test_get_currency_sell_rate(self, _get_currency_rates_mock):
        _get_currency_rates_mock.return_value = self.currency_rates_value

        assert self.adapter.get_currency_sell_rate("USD") == 4.0562

    @patch("currencies.nbp_adapter.NBPExchangeRatesAdapter._get_currency_rates")
    def test_returns_none_when_not_data(self, _get_currency_rates_mock):
        _get_currency_rates_mock.return_value = {}

        assert not self.adapter.get_currency_buy_rate("USD")
        assert not self.adapter.get_currency_sell_rate("USD")

    @patch("currencies.nbp_adapter.requests.get")
    def test_get_currency_rates_not_returns_status_code_200(self, requests_get_mock):
        requests_get_mock.return_value = Mock(status_code=400)

        assert not self.adapter._get_currency_rates("USD")
