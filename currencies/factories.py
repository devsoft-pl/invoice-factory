import datetime

import factory
from factory import fuzzy

from currencies.models import Currency, ExchangeRate
from users.factories import UserFactory


class CurrencyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Currency

    code = factory.Sequence(lambda n: "Code %03d" % n)
    user = factory.SubFactory(UserFactory)


class ExchangeRateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ExchangeRate

    buy_rate = fuzzy.FuzzyDecimal(0.4, 1.4)
    sell_rate = fuzzy.FuzzyDecimal(1.5, 2.5)
    date = fuzzy.FuzzyDate(datetime.date(2023, 1, 8))
    currency = factory.SubFactory(CurrencyFactory)
