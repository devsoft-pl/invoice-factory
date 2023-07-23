import pytest

from companies.factories import CompanyFactory
from currencies.factories import CurrencyFactory
from invoices.factories import InvoiceDictFactory
from invoices.serializers import InvoiceSerializer
from items.factories import ItemDictFactory
from users.factories import UserFactory
from vat_rates.factories import VatRateFactory


@pytest.mark.django_db
class TestCreateInvoice:
    @pytest.fixture(autouse=True)
    def set_up(self):
        self.user = UserFactory()
        self.company = CompanyFactory()
        self.client = CompanyFactory()
        self.currency = CurrencyFactory()
        self.vat = VatRateFactory()
        self.items_data = ItemDictFactory.create_batch(
            size=3, user=self.user, vat=self.vat
        )
        self.invoice_data = InvoiceDictFactory(
            user=self.user, company=self.company, client=self.client
        )

    def test_create_invoice_if_valid_data(self):
        validated_data = self.invoice_data.copy()
        validated_data["items"] = self.items_data

        serializer = InvoiceSerializer()
        invoice = serializer.create(validated_data)

        assert invoice.pk
        assert invoice.invoice_number == validated_data["invoice_number"]
        assert invoice.items.count() == 3
