import factory

from currencies.models import Currency
from users.factories import UserFactory


class CurrencyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Currency

    code = factory.Sequence(lambda n: "Code %03d" % n)
    user = user = factory.SubFactory(UserFactory)
