import factory
from factory.fuzzy import FuzzyInteger

from users.factories import UserFactory
from vat_rates.models import VatRate


class VatRateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = VatRate

    rate = factory.Sequence(lambda n: n+1)
    user = factory.SubFactory(UserFactory)
