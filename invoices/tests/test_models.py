import pytest

from companies.models import Company
from countries.models import Country
from currencies.models import Currency
from invoices.models import Invoice


@pytest.mark.django_db
class TestInvoiceModel:
    @pytest.fixture(autouse=True)
    def set_up(self):
        country = Country.objects.create(country="Polska")
        currency = Currency.objects.create(code="pln")
        company = Company.objects.create(
            name="Test Firma",
            nip="1111111111",
            regon="1111111",
            country=country,
            address="Testowa 1",
            zip_code="11-111",
            city="Testowa",
            email="test@test.pl",
            phone_number="999999999",
        )
        client = Company.objects.create(
            name="Test Firma Kontrahent",
            nip="2222222222",
            regon="2222222",
            country=country,
            address="Testowa 2",
            zip_code="22-22",
            city="Testowa 2",
            email="test2@test2.pl",
            phone_number="888888888",
        )
        self.invoice = Invoice.objects.create(
            invoice_number="1/2022",
            invoice_type=0,
            company=company,
            create_date="2023-01-01",
            sale_date="2023-01-01",
            payment_date="2023-01-07",
            payment_method=0,
            currency=currency,
            account_number="1111111111111111",
            client=client,
        )

    def test_str_returns_item_name(self):
        assert self.invoice.__str__() == self.invoice.invoice_number
