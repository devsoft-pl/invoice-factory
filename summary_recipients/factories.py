import factory
from factory import fuzzy

from companies.factories import CompanyFactory
from summary_recipients.models import SummaryRecipient


class SummaryRecipientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SummaryRecipient

    description = factory.Sequence(lambda n: "Description %03d" % n)
    company = factory.SubFactory(CompanyFactory)
    day = fuzzy.FuzzyInteger(1, 28)
    email = factory.Sequence(lambda n: "test_%03d@test.pl" % n)
    settlement_types = SummaryRecipient.MONTHLY
    final_call = factory.fuzzy.FuzzyChoice([True, False])
    is_last_day = factory.fuzzy.FuzzyChoice([True, False])


class SummaryRecipientDictFactory(factory.DictFactory):
    description = factory.Sequence(lambda n: "Description %03d" % n)
    day = fuzzy.FuzzyInteger(1, 28)
    email = factory.Sequence(lambda n: "test_%03d@test.pl" % n)
    settlement_types = SummaryRecipient.MONTHLY
    final_call = factory.fuzzy.FuzzyChoice([True, False])
    is_last_day = factory.fuzzy.FuzzyChoice([True, False])
