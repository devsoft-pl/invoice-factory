import factory
from django.contrib.auth.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: "User%03d" % n)
    email = factory.Sequence(lambda n: "test_%03d@test.pl" % n)


class UserDictFactory(factory.DictFactory):
    username = factory.Sequence(lambda n: "user%03d" % n)
    password = factory.Sequence(lambda n: "password%03d" % n)
    email = factory.Sequence(lambda n: "test_%03d@test.pl" % n)
