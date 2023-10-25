import factory
from factory import fuzzy

from companies.models import Company, SummaryRecipient
from countries.factories import CountryFactory
from users.factories import UserFactory


class CompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Company

    name = factory.Sequence(lambda n: "Company %03d" % n)
    nip = factory.Sequence(lambda n: "Nip %03d" % n)
    regon = factory.Sequence(lambda n: "Regon %03d" % n)
    country = factory.SubFactory(CountryFactory)
    address = factory.Sequence(lambda n: "Address %03d" % n)
    zip_code = factory.Sequence(lambda n: "Zip %03d" % n)
    city = factory.Sequence(lambda n: "City %03d" % n)
    email = factory.Sequence(lambda n: "test_%03d@test.pl" % n)
    phone_number = factory.Sequence(lambda n: "Phone %03d" % n)
    is_my_company = factory.fuzzy.FuzzyChoice([True, False])
    user = factory.SubFactory(UserFactory)


class CompanyDictFactory(factory.DictFactory):
    name = factory.Sequence(lambda n: "Company %03d" % n)
    nip = factory.Sequence(lambda n: "Nip %03d" % n)
    regon = factory.Sequence(lambda n: "Regon %03d" % n)
    address = factory.Sequence(lambda n: "Address %03d" % n)
    zip_code = factory.Sequence(lambda n: "Zip %03d" % n)
    city = factory.Sequence(lambda n: "City %03d" % n)
    email = factory.Sequence(lambda n: "test_%03d@test.pl" % n)
    phone_number = factory.Sequence(lambda n: "Phone %03d" % n)
    is_my_company = factory.fuzzy.FuzzyChoice([True, False])


class SummaryRecipientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SummaryRecipient

    description = factory.Sequence(lambda n: "Description %03d" % n)
    company = factory.SubFactory(CompanyFactory)
    day = fuzzy.FuzzyInteger(1, 28)
    email = factory.Sequence(lambda n: "test_%03d@test.pl" % n)
    settlement_types = SummaryRecipient.MONTHLY


class SummaryRecipientDictFactory(factory.DictFactory):
    description = factory.Sequence(lambda n: "Description %03d" % n)
    day = fuzzy.FuzzyInteger(1, 28)
    email = factory.Sequence(lambda n: "test_%03d@test.pl" % n)
    settlement_types = SummaryRecipient.MONTHLY
