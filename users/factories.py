import factory

from users.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: "test_%03d@test.pl" % n)


class UserDictFactory(factory.DictFactory):
    password = factory.Sequence(lambda n: "password%03d" % n)
    email = factory.Sequence(lambda n: "test_%03d@test.pl" % n)
