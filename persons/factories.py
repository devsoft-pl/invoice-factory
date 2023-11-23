import factory

from countries.factories import CountryFactory
from persons.models import Person
from users.factories import UserFactory


class PersonFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Person

    first_name = factory.Sequence(lambda n: "First name %03d" % n)
    last_name = factory.Sequence(lambda n: "Last name %03d" % n)
    address = factory.Sequence(lambda n: "Address %03d" % n)
    zip_code = factory.Sequence(lambda n: "Zip %03d" % n)
    city = factory.Sequence(lambda n: "City %03d" % n)
    country = factory.SubFactory(CountryFactory)
    email = factory.Sequence(lambda n: "test_%03d@test.pl" % n)
    phone_number = factory.Sequence(lambda n: "Phone %03d" % n)
    user = factory.SubFactory(UserFactory)


class PersonDictFactory(factory.DictFactory):
    first_name = factory.Sequence(lambda n: "First name %03d" % n)
    last_name = factory.Sequence(lambda n: "Last name %03d" % n)
    address = factory.Sequence(lambda n: "Address %03d" % n)
    zip_code = factory.Sequence(lambda n: "Zip %03d" % n)
    city = factory.Sequence(lambda n: "City %03d" % n)
    email = factory.Sequence(lambda n: "test_%03d@test.pl" % n)
    phone_number = factory.Sequence(lambda n: "Phone %03d" % n)
