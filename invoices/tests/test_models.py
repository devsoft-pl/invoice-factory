import datetime
from decimal import Decimal

import pytest

from companies.factories import CompanyFactory
from currencies.factories import CurrencyFactory, ExchangeRateFactory
from invoices.factories import (
    CorrectionInvoiceRelationFactory,
    InvoiceBuyFactory,
    InvoiceSellFactory,
    InvoiceSellPersonFactory,
    YearFactory,
)
from invoices.models import Invoice, Year
from items.factories import ItemFactory
from persons.factories import PersonFactory
from users.factories import UserFactory
from vat_rates.factories import VatRateFactory


@pytest.mark.django_db
class TestInvoiceModel:
    @pytest.fixture(autouse=True)
    def set_up(self):
        self.invoice = InvoiceSellFactory.create()
        self.invoice_2 = InvoiceSellFactory.create()
        vat = VatRateFactory.create(rate=23)
        self.item = ItemFactory.create(
            invoice=self.invoice, amount=2, net_price=1200, vat=vat
        )
        self.item_2 = ItemFactory.create(
            invoice=self.invoice, amount=1, net_price=800, vat=vat
        )
        self.invoice.update_totals()
        self.invoice.refresh_from_db()

    def test_returns_str_item_name(self):
        assert self.invoice.__str__() == self.invoice.invoice_number

    def test_returns_recurring_invoice_name(self):
        self.invoice = InvoiceSellFactory.create(invoice_number="")
        assert self.invoice.__str__() == "Recurring"

    def test_returns_calculated_net_amount(self):
        assert self.invoice.calculate_net_amount() == Decimal("3200")

    def test_returns_zero_calculated_net_amount_if_no_items(self):
        assert self.invoice_2.calculate_net_amount() == Decimal("0")

    def test_returns_tax_amount(self):
        assert self.invoice.tax_amount == Decimal("736")

    def test_returns_zero_tax_amount_if_no_items(self):
        assert self.invoice_2.tax_amount == Decimal("0")

    def test_returns_calculated_gross_amount(self):
        assert self.invoice.calculate_gross_amount() == Decimal("3936")

    def test_returns_zero_calculated_gross_amount_if_no_items(self):
        assert self.invoice_2.calculate_gross_amount() == Decimal("0")

    def test_returns_sell_rate_in_pln(self):
        exchange_rate = ExchangeRateFactory.create(
            currency=self.invoice.currency,
            date=self.invoice.sale_date,
        )

        assert exchange_rate.sell_rate == self.invoice.sell_rate_in_pln

    def test_returns_invoice_sale(self):
        assert self.invoice.is_sell

    def test_returns_true_when_has_items(self):
        assert self.invoice.has_items

    def test_returns_false_when_no_items(self):
        invoice = InvoiceSellFactory.create()
        assert not invoice.has_items

    def test_invoice_has_correction_invoice_relation_exists(self):
        correction_invoice = InvoiceSellFactory.create()
        original_invoice = InvoiceSellFactory.create()

        CorrectionInvoiceRelationFactory(
            invoice=original_invoice, correction_invoice=correction_invoice
        )

        assert correction_invoice.has_correction_invoice
        assert not original_invoice.has_correction_invoice

    def test_invoice_does_not_have_correction_invoice_relation(self):
        assert not self.invoice.has_correction_invoice

    def test_has_item_with_vat_returns_true(self):
        assert self.invoice.has_item_with_vat

    def test_has_item_with_vat_returns_false(self):
        invoice = InvoiceSellFactory.create()
        vat_zero = VatRateFactory.create(rate=0)
        ItemFactory.create(invoice=invoice, vat=vat_zero)

        assert not invoice.has_item_with_vat

    def test_sell_rate_in_pln_returns_one_for_pln_currency(self):
        pln = CurrencyFactory.create(code="PLN")
        invoice = InvoiceSellFactory.create(currency=pln)

        assert invoice.sell_rate_in_pln == 1

    def test_sell_rate_returns_none_if_no_rate_found_for_foreign_currency(self):
        usd = CurrencyFactory.create(code="USD")
        invoice = InvoiceSellFactory.create(currency=usd)

        assert invoice.sell_rate_in_pln is None

    def test_items_are_deleted_when_invoice_is_deleted(self):
        invoice = InvoiceSellFactory.create()
        ItemFactory.create(invoice=invoice)

        assert invoice.items.count() == 1

        invoice.delete()

        from items.models import Item

        assert Item.objects.filter(invoice=invoice.pk).count() == 0

    def test_returns_false_if_invoice_is_buy(self):
        invoice = InvoiceBuyFactory.create()
        assert invoice.is_sell is False
        assert invoice.invoice_type == Invoice.INVOICE_PURCHASE

    def test_is_owned_by(self):
        user = UserFactory()
        company = CompanyFactory(user=user)
        person = PersonFactory(user=user)
        other_user = UserFactory()

        invoice_company = InvoiceSellFactory(company=company)
        invoice_person = InvoiceSellPersonFactory(person=person, company=None)

        assert invoice_company.is_owned_by(user) is True
        assert invoice_person.is_owned_by(user) is True
        assert invoice_company.is_owned_by(other_user) is False
        assert invoice_person.is_owned_by(other_user) is False

    def test_update_totals(self):
        invoice = InvoiceSellFactory.create(net_amount=0, gross_amount=0)
        vat = VatRateFactory.create(rate=23)
        ItemFactory.create(
            invoice=invoice, amount=2, net_price=Decimal("100.00"), vat=vat
        )
        ItemFactory.create(
            invoice=invoice, amount=1, net_price=Decimal("50.00"), vat=vat
        )

        invoice.update_totals()
        invoice.refresh_from_db()

        expected_net = Decimal("250.00")
        expected_gross = expected_net * Decimal("1.23")

        assert invoice.net_amount == expected_net
        assert invoice.gross_amount == expected_gross

    def test_update_totals_with_no_items(self):
        invoice = InvoiceSellFactory.create(net_amount=100, gross_amount=123)
        invoice.update_totals()
        invoice.refresh_from_db()

        assert invoice.net_amount == Decimal("0.00")
        assert invoice.gross_amount == Decimal("0.00")


@pytest.mark.django_db
class TestYearModel:
    @pytest.fixture(autouse=True)
    def set_up(self):
        self.year = YearFactory.create()

    def test_returns_str_for_year(self):
        assert self.year.__str__() == str(self.year.year)


@pytest.mark.django_db
class TestYearManagement:
    def test_creates_year_for_company_user_on_invoice_create(self):
        user = UserFactory()
        company = CompanyFactory(user=user)

        InvoiceSellFactory(company=company, sale_date=datetime.date(2024, 5, 10))

        assert Year.objects.filter(year=2024, user=user).exists()

    def test_creates_year_for_person_user_on_invoice_create(self):
        user = UserFactory()
        person = PersonFactory(user=user)

        InvoiceSellPersonFactory(
            person=person, company=None, sale_date=datetime.date(2025, 1, 15)
        )

        assert Year.objects.filter(year=2025, user=user).exists()

    def test_does_not_duplicate_year_for_same_user(self):
        user = UserFactory()
        company = CompanyFactory(user=user)

        InvoiceSellFactory(company=company, sale_date=datetime.date(2024, 1, 1))
        InvoiceSellFactory(company=company, sale_date=datetime.date(2024, 12, 31))

        assert Year.objects.filter(year=2024, user=user).count() == 1

    def test_creates_separate_years_for_different_users(self):
        user_a = UserFactory()
        company_a = CompanyFactory(user=user_a)
        InvoiceSellFactory(company=company_a, sale_date=datetime.date(2024, 1, 1))

        user_b = UserFactory()
        company_b = CompanyFactory(user=user_b)
        InvoiceSellFactory(company=company_b, sale_date=datetime.date(2024, 1, 1))

        assert Year.objects.filter(year=2024).count() == 2
        assert Year.objects.filter(year=2024, user=user_a).exists()
        assert Year.objects.filter(year=2024, user=user_b).exists()

    def test_orphaned_year_is_deleted_after_invoice_update(self):
        user = UserFactory()
        future_date = datetime.date(2026, 5, 10)
        invoice = InvoiceSellFactory.create(
            company__user=user,
            sale_date=future_date,
            payment_date=future_date + datetime.timedelta(days=7),
            is_recurring=False,
        )

        assert Year.objects.filter(year=2026, user=user).exists()

        invoice.sale_date = datetime.date(2024, 5, 10)
        invoice.save()

        assert Year.objects.filter(year=2024, user=user).exists()
        assert not Year.objects.filter(year=2026, user=user).exists()

    def test_year_is_not_deleted_on_update_if_other_invoices_exist(self):
        user = UserFactory()
        future_date = datetime.date(2026, 5, 10)
        invoice_to_edit = InvoiceSellFactory.create(
            company__user=user,
            sale_date=future_date,
            payment_date=future_date + datetime.timedelta(days=7),
            is_recurring=False,
        )
        InvoiceSellFactory.create(
            company__user=user,
            sale_date=future_date.replace(month=11),
            payment_date=future_date + datetime.timedelta(days=7),
            is_recurring=False,
        )

        assert Year.objects.filter(year=2026, user=user).exists()

        invoice_to_edit.sale_date = datetime.date(2024, 5, 10)
        invoice_to_edit.save()

        assert Year.objects.filter(year=2024, user=user).exists()
        assert Year.objects.filter(year=2026, user=user).exists()

    def test_year_is_deleted_after_last_invoice_is_deleted(self):
        user = UserFactory()
        future_date = datetime.date(2027, 1, 1)
        invoice = InvoiceSellFactory.create(
            company__user=user,
            sale_date=future_date,
            payment_date=future_date + datetime.timedelta(days=7),
            is_recurring=False,
        )

        assert Year.objects.filter(year=2027, user=user).exists()

        invoice.delete()

        assert not Year.objects.filter(year=2027, user=user).exists()

    def test_year_is_not_deleted_on_delete_if_other_invoices_exist(self):
        user = UserFactory()
        future_date = datetime.date(2028, 1, 1)
        invoice_to_delete = InvoiceSellFactory.create(
            company__user=user,
            sale_date=future_date,
            payment_date=future_date + datetime.timedelta(days=7),
            is_recurring=False,
        )
        InvoiceSellFactory.create(
            company__user=user,
            sale_date=future_date.replace(month=2),
            payment_date=future_date + datetime.timedelta(days=7),
            is_recurring=False,
        )

        assert Year.objects.filter(year=2028, user=user).exists()

        invoice_to_delete.delete()

        assert Year.objects.filter(year=2028, user=user).exists()


@pytest.mark.django_db
class TestCorrectionInvoiceRelationModel:
    @pytest.fixture(autouse=True)
    def set_up(self):
        self.invoice = InvoiceSellFactory.create(invoice_number="1/2024")
        self.correction_invoice = InvoiceSellFactory.create(invoice_number="1/k/2024")
        self.correction_invoice_relation = CorrectionInvoiceRelationFactory.create(
            invoice=self.invoice, correction_invoice=self.correction_invoice
        )

    def test_returns_str_invoice_number(self):
        assert (
            self.correction_invoice_relation.__str__()
            == f"{self.correction_invoice_relation.invoice.invoice_number}, "
            f"{self.correction_invoice_relation.correction_invoice.invoice_number}"
        )
