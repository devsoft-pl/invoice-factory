import pytest

from companies.factories import CompanyFactory
from currencies.factories import CurrencyFactory
from invoices.factories import InvoiceDictFactory, InvoiceFactory
from invoices.serializers import InvoiceSerializer
from items.factories import ItemDictFactory, ItemFactory
from users.factories import UserFactory
from vat_rates.factories import VatRateFactory


@pytest.mark.django_db
class TestInvoiceSerializer:
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
        self.invoice = InvoiceFactory()

    def test_create_if_valid_data(self):
        validated_data = self.invoice_data.copy()
        validated_data["items"] = self.items_data

        serializer = InvoiceSerializer()
        invoice = serializer.create(validated_data)

        assert invoice.pk
        assert invoice.invoice_number == validated_data["invoice_number"]
        assert invoice.items.count() == 3

    def test_update_if_valid_data(self):
        validated_data = self.invoice_data.copy()
        item = ItemFactory(invoice=self.invoice)
        item_data = ItemDictFactory(id=item.pk, user=self.user, vat=self.vat)
        validated_data["items"] = [item_data]
        serializer = InvoiceSerializer()
        invoice = serializer.update(self.invoice, validated_data)

        assert invoice.invoice_number == validated_data["invoice_number"]
        assert invoice.items.all()[0].pk == item.pk
        assert invoice.items.count() == 1
