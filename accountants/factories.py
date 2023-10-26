import factory

from accountants.models import Accountant
from users.factories import UserFactory


class AccountantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Accountant

    name = factory.Sequence(lambda n: "Name %03d" % n)
    email = factory.Sequence(lambda n: "test_%03d@test.pl" % n)
    phone_number = factory.Sequence(lambda n: "Phone %03d" % n)
    user = factory.SubFactory(UserFactory)


class AccountantDictFactory(factory.DictFactory):
    name = factory.Sequence(lambda n: "Name %03d" % n)
    email = factory.Sequence(lambda n: "test_%03d@test.pl" % n)
    phone_number = factory.Sequence(lambda n: "Phone %03d" % n)