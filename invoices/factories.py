import datetime

import factory
from factory import fuzzy

from companies.factories import CompanyFactory
from currencies.factories import CurrencyFactory
from invoices.models import Invoice
from users.factories import UserFactory


class InvoiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Invoice

    invoice_number = factory.Sequence(lambda n: "Invoice number %03d" % n)
    invoice_type = factory.fuzzy.FuzzyChoice(
        Invoice.INVOICE_TYPES, getter=lambda i: i[0]
    )
    company = factory.SubFactory(CompanyFactory)
    create_date = fuzzy.FuzzyDate(datetime.date(2023, 1, 1))
    sale_date = fuzzy.FuzzyDate(datetime.date(2023, 1, 1))
    payment_date = factory.Faker(
        "date_between_dates", date_start=factory.SelfAttribute("..sale_date")
    )
    payment_method = factory.fuzzy.FuzzyChoice(
        Invoice.PAYMENT_METHOD, getter=lambda p: p[0]
    )
    currency = factory.SubFactory(CurrencyFactory)
    account_number = factory.Sequence(lambda n: "Account number %03d" % n)
    client = factory.SubFactory(CompanyFactory)
    user = factory.SubFactory(UserFactory)


class InvoiceDictFactory(factory.DictFactory):
    invoice_number = factory.Sequence(lambda n: "Invoice number %03d" % n)
    invoice_type = factory.fuzzy.FuzzyChoice(
        Invoice.INVOICE_TYPES, getter=lambda i: i[0]
    )
    create_date = fuzzy.FuzzyDate(datetime.date(2023, 1, 1))
    sale_date = fuzzy.FuzzyDate(datetime.date(2023, 1, 1))
    payment_date = factory.Faker(
        "date_between_dates", date_start=factory.SelfAttribute("..sale_date")
    )
    payment_method = factory.fuzzy.FuzzyChoice(
        Invoice.PAYMENT_METHOD, getter=lambda p: p[0]
    )
    account_number = factory.Sequence(lambda n: "Account number %03d" % n)
