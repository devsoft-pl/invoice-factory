import factory
from factory.fuzzy import FuzzyInteger

from users.factories import UserFactory
from vat_rates.models import VatRate


class VatRateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = VatRate

    rate = FuzzyInteger(0, 23)
    user = factory.SubFactory(UserFactory)
