import factory

from users.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: "test_%03d@test.pl" % n)
    first_name = factory.Sequence(lambda n: "Test imie%03d" % n)
    last_name = factory.Sequence(lambda n: "Test nazwisko%03d" % n)


class UserDictFactory(factory.DictFactory):
    password = factory.Sequence(lambda n: "password%03d" % n)
    email = factory.Sequence(lambda n: "test_%03d@test.pl" % n)
