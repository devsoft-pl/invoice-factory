import datetime

import factory
from factory import fuzzy

from companies.factories import CompanyFactory
from currencies.factories import CurrencyFactory
from invoices.models import Invoice
from persons.factories import PersonFactory


class InvoiceSellFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Invoice

    invoice_number = factory.Sequence(lambda n: "Invoice number %03d" % n)
    invoice_type = Invoice.INVOICE_SALES
    company = factory.SubFactory(CompanyFactory)
    client = factory.SubFactory(CompanyFactory)
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
    is_recurring = factory.fuzzy.FuzzyChoice([True, False])
    is_settled = factory.fuzzy.FuzzyChoice([True, False])


class InvoiceSellPersonFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Invoice

    invoice_number = factory.Sequence(lambda n: "Invoice number %03d" % n)
    invoice_type = Invoice.INVOICE_SALES
    company = factory.SubFactory(CompanyFactory)
    person = factory.SubFactory(PersonFactory)
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
    is_recurring = factory.fuzzy.FuzzyChoice([True, False])
    is_settled = factory.fuzzy.FuzzyChoice([True, False])


class InvoiceBuyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Invoice

    invoice_number = factory.Sequence(lambda n: "Invoice number %04d" % n)
    invoice_type = Invoice.INVOICE_PURCHASE
    company = factory.SubFactory(CompanyFactory)
    sale_date = fuzzy.FuzzyDate(datetime.date(2023, 1, 1))
    payment_date = factory.Faker(
        "date_between_dates", date_start=factory.SelfAttribute("..sale_date")
    )
    settlement_date = factory.Faker(
        "date_between_dates", date_start=factory.SelfAttribute("..payment_date")
    )
    invoice_file = factory.django.FileField(filename="the_file.pdf", data="test")
    is_settled = factory.fuzzy.FuzzyChoice([True, False])


class InvoiceSellDictFactory(factory.DictFactory):
    invoice_number = factory.Sequence(lambda n: "Invoice number %03d" % n)
    invoice_type = Invoice.INVOICE_SALES
    create_date = fuzzy.FuzzyDate(datetime.date(2023, 1, 1))
    sale_date = fuzzy.FuzzyDate(datetime.date(2023, 1, 1))
    payment_date = factory.Faker(
        "date_between_dates", date_start=factory.SelfAttribute("..sale_date")
    )
    payment_method = factory.fuzzy.FuzzyChoice(
        Invoice.PAYMENT_METHOD, getter=lambda p: p[0]
    )
    account_number = factory.Sequence(lambda n: "Account number %03d" % n)
    is_recurring = factory.fuzzy.FuzzyChoice([True, False])
    is_settled = factory.fuzzy.FuzzyChoice([True, False])


class InvoiceBuyDictFactory(factory.DictFactory):
    invoice_number = factory.Sequence(lambda n: "Invoice number %03d" % n)
    invoice_type = Invoice.INVOICE_PURCHASE
    sale_date = fuzzy.FuzzyDate(datetime.date(2023, 1, 1))
    payment_date = factory.Faker(
        "date_between_dates", date_start=factory.SelfAttribute("..sale_date")
    )
    settlement_date = factory.Faker(
        "date_between_dates", date_start=factory.SelfAttribute("..payment_date")
    )
    invoice_file = factory.django.FileField(filename="the_file.pdf", data="test")
    is_settled = factory.fuzzy.FuzzyChoice([True, False])
