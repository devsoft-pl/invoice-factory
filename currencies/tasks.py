import logging
from datetime import datetime

from base.celery import app
from currencies.models import Currency, ExchangeRate
from currencies.nbp_adapter import NBPExchangeRatesAdapter

logger = logging.getLogger(__name__)


@app.task(name="get_exchange_rates_for_all")
def get_exchange_rates_for_all():
    logger.info("Trying to fetch all exchange rates")

    currencies = Currency.objects.all()

    for currency in currencies:
        get_exchange_rate_for_currency.apply_async(args=[currency.id])


@app.task(name="get_exchange_rate_for_currency")
def get_exchange_rate_for_currency(instance_id):
    logger.info("Trying to fetch exchange rate for currency")

    adapter = NBPExchangeRatesAdapter()
    currency = Currency.objects.get(pk=instance_id)
    date = datetime.today()

    logger.info(
        f"Trying to fetch {currency.code} for date {date} and user {currency.user}"
    )

    buy_rate = adapter.get_currency_buy_rate(currency.code.lower())
    sell_rate = adapter.get_currency_sell_rate(currency.code.lower())

    if buy_rate and sell_rate:
        if not ExchangeRate.objects.filter(
            date=date, currency=currency, currency__user=currency.user
        ).count():
            ExchangeRate.objects.create(
                buy_rate=buy_rate, sell_rate=sell_rate, date=date, currency=currency
            )
