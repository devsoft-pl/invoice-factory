import factory

from users.factories import UserFactory
from vat_rates.models import VatRate


class VatRateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = VatRate

    rate = factory.Sequence(lambda n: n + 1)
    user = factory.SubFactory(UserFactory)


class VatRateDictFactory(factory.DictFactory):
    rate = factory.Sequence(lambda n: n + 1)
