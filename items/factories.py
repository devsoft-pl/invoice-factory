import factory
from factory import fuzzy

from invoices.factories import InvoiceSellFactory
from items.models import Item
from users.factories import UserFactory
from vat_rates.factories import VatRateFactory


class ItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Item

    invoice = factory.SubFactory(InvoiceSellFactory)
    name = factory.Sequence(lambda n: "Name %03d" % n)
    pkwiu = factory.Sequence(lambda n: "PKWIU %03d" % n)
    amount = fuzzy.FuzzyInteger(1, 5)
    net_price = fuzzy.FuzzyDecimal(100, 10000)
    vat = factory.SubFactory(VatRateFactory)
    user = factory.SubFactory(UserFactory)


class ItemDictFactory(factory.DictFactory):
    name = factory.Sequence(lambda n: "Name %03d" % n)
    pkwiu = factory.Sequence(lambda n: "PKWIU %03d" % n)
    amount = fuzzy.FuzzyInteger(1, 5)
    net_price = fuzzy.FuzzyDecimal(100, 10000)
