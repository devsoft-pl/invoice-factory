import requests


class NBPExchangeRatesAdapter:
    base_url = "http://api.nbp.pl/api/"

    def _get_currency_rates(self, currency_code):
        url = f"{self.base_url}exchangerates/rates/c/{currency_code}/"
        response = requests.get(url, headers={"Accept": "application/json"})
        if not response.status_code == 200:
            return None

        return response.json()

    def get_currency_buy_rate(self, currency_code):
        data = self._get_currency_rates(currency_code)
        if not data:
            return None

        return data["rates"][0]["bid"]

    def get_currency_sell_rate(self, currency_code):
        data = self._get_currency_rates(currency_code)
        if not data:
            return None

        return data["rates"][0]["ask"]


if __name__ == "__main__":  # pragma: no cover
    adapter = NBPExchangeRatesAdapter()
    currency_buy_rate = adapter.get_currency_buy_rate("usd")
    print(f"Kurs kupna: {currency_buy_rate}")

    currency_sell_rate = adapter.get_currency_sell_rate("usd")
    print(f"Kurs sprzedaży: {currency_sell_rate}")
