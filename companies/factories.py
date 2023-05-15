import factory

from companies.models import Company
from countries.factories import CountryFactory
from users.factories import UserFactory


class MyCompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Company

    name = factory.Sequence(lambda n: "Company %03d" % n)
    nip = factory.Sequence(lambda n: "My Nip %03d" % n)
    regon = factory.Sequence(lambda n: "My Regon %03d" % n)
    country = factory.SubFactory(CountryFactory)
    address = factory.Sequence(lambda n: "Address %03d" % n)
    zip_code = factory.Sequence(lambda n: "Zip %03d" % n)
    city = factory.Sequence(lambda n: "City %03d" % n)
    email = factory.Sequence(lambda n: "test_%03d@test.pl" % n)
    phone_number = factory.Sequence(lambda n: "Phone %03d" % n)
    user = factory.SubFactory(UserFactory)
    is_my_company = True


class ClientCompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Company

    name = factory.Sequence(lambda n: "Client %03d" % n)
    nip = factory.Sequence(lambda n: "Client Nip %03d" % n)
    regon = factory.Sequence(lambda n: "Client Regon %03d" % n)
    country = factory.SubFactory(CountryFactory)
    address = factory.Sequence(lambda n: "Address %03d" % n)
    zip_code = factory.Sequence(lambda n: "Zip code %03d" % n)
    city = factory.Sequence(lambda n: "City %03d" % n)
    email = factory.Sequence(lambda n: "test_%03d@test.pl" % n)
    phone_number = factory.Sequence(lambda n: "Phone %03d" % n)
    user = factory.SubFactory(UserFactory)
    is_my_company = False
