import factory

from currencies.models import Currency


class CurrencyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Currency

    code = factory.Sequence(lambda n: "Code %03d" % n)
