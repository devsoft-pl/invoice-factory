import datetime

import factory
from factory import fuzzy
from factory.fuzzy import FuzzyInteger

from companies.factories import ClientCompanyFactory, MyCompanyFactory
from currencies.factories import CurrencyFactory
from invoices.models import Invoice
from users.factories import UserFactory


class InvoiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Invoice

    invoice_number = factory.Sequence(lambda n: "Invoice number %03d" % n)
    invoice_type = FuzzyInteger(0, 1)
    company = factory.SubFactory(MyCompanyFactory)
    create_date = fuzzy.FuzzyDate(datetime.date(2023, 1, 1))
    sale_date = fuzzy.FuzzyDate(datetime.date(2023, 1, 1))
    payment_date = factory.Faker(
        "date_between_dates", date_start=factory.SelfAttribute("..sale_date")
    )
    payment_method = FuzzyInteger(0, 1)
    currency = factory.SubFactory(CurrencyFactory)
    account_number = factory.Sequence(lambda n: "Account number %03d" % n)
    client = factory.SubFactory(ClientCompanyFactory)
    user = factory.SubFactory(UserFactory)
