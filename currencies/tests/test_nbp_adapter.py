from unittest.mock import patch

import pytest

from currencies.nbp.adapter import NBPExchangeRatesAdapter


class TestNBPExchangeRatesAdapter:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.adapter = NBPExchangeRatesAdapter()

    @patch("currencies.nbp.adapter.NBPExchangeRatesAdapter._get_currency_rates")
    def test_get_currency_buy_rate(self, _get_currency_rates_mock):
        _get_currency_rates_mock.return_value = {
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

        assert self.adapter.get_currency_buy_rate("USD") == 3.9758

    @patch("currencies.nbp.adapter.NBPExchangeRatesAdapter._get_currency_rates")
    def test_get_currency_sell_rate(self, _get_currency_rates_mock):
        _get_currency_rates_mock.return_value = {
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

        assert self.adapter.get_currency_sell_rate("USD") == 4.0562
