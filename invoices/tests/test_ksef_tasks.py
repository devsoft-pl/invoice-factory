import datetime
from unittest.mock import patch

import pytest
from django.utils import timezone

from companies.factories import CompanyFactory
from currencies.factories import CurrencyFactory
from invoices.models import Invoice
from invoices.tasks import _save_ksef_invoice, fetch_purchase_invoices_from_ksef
from items.models import Item
from vat_rates.factories import VatRateFactory


@pytest.fixture(autouse=True)
def setup_ksef_settings(settings):
    settings.KSEF_API_URL_TEST = "http://test-ksef-api.com"
    settings.KSEF_API_URL_PRODUCTION = "http://prod-ksef-api.com"
    settings.KSEF_IS_TEST = True


@pytest.fixture
def mock_ksef_adapter():
    with patch("invoices.tasks.KSeFAdapter") as MockAdapter:
        adapter_instance = MockAdapter.return_value
        adapter_instance.__enter__.return_value = adapter_instance
        adapter_instance.authenticate.return_value = True
        yield adapter_instance


@pytest.fixture
def mock_ksef_mapper():
    with patch("invoices.tasks.map_ksef_invoice_to_dict") as mock_to_dict, patch(
        "invoices.tasks.map_ksef_invoice_to_items"
    ) as mock_to_items:
        mock_to_dict.return_value = {
            "invoice_number": "KSEF/123/2026",
            "invoice_type": Invoice.INVOICE_PURCHASE,
            "sale_date": datetime.date(2026, 4, 1),
            "create_date": datetime.date(2026, 4, 1),
            "payment_date": datetime.date(2026, 4, 1),
            "settlement_date": datetime.date(2026, 4, 1),
            "net_amount": 100.00,
            "gross_amount": 123.00,
            "is_recurring": False,
            "is_settled": False,
            "is_paid": False,
            "account_number": "1234567890",
            "payment_method": Invoice.BANK_TRANSFER,
        }
        mock_to_items.return_value = [
            {"name": "Item 1", "amount": 1, "net_price": 100.00, "vat_rate": 23}
        ]
        yield mock_to_dict, mock_to_items


@pytest.mark.django_db
class TestFetchPurchaseInvoicesFromKSeFTask:
    @pytest.fixture(autouse=True)
    def setup(self, setup_ksef_settings):
        self.company = CompanyFactory(
            is_my_company=True, ksef_token="test_token", nip="1234567890"
        )
        self.user = self.company.user
        self.currency = CurrencyFactory(code="PLN", user=self.user)
        self.vat_rate = VatRateFactory(rate=23, user=self.user)

    def test_task_authenticates_and_fetches_invoices(
        self, mock_ksef_adapter, mock_ksef_mapper
    ):
        ksef_invoice_data = {
            "ksefNumber": "KSEF_NUM_1",
            "invoiceNumber": "INV/001",
            "issueDate": "2026-04-01",
            "acquisitionDate": "2026-04-01T10:00:00Z",
            "netAmount": 100.00,
            "grossAmount": 123.00,
            "currency": "PLN",
        }
        mock_ksef_adapter.get_all_purchase_invoices.return_value = [[ksef_invoice_data]]
        mock_ksef_adapter.get_invoice_xml.return_value = "<xml>invoice</xml>"

        fetch_purchase_invoices_from_ksef()

        mock_ksef_adapter.authenticate.assert_called_once()
        mock_ksef_adapter.get_all_purchase_invoices.assert_called_once()
        mock_ksef_adapter.get_invoice_xml.assert_called_once_with("KSEF_NUM_1")
        assert Invoice.objects.count() == 1
        assert Item.objects.count() == 1
        self.company.refresh_from_db()
        assert self.company.ksef_last_fetched_at.date() == timezone.now().date()

    def test_task_handles_authentication_failure(self, mock_ksef_adapter):
        mock_ksef_adapter.authenticate.return_value = False

        fetch_purchase_invoices_from_ksef()

        mock_ksef_adapter.authenticate.assert_called_once()
        mock_ksef_adapter.get_all_purchase_invoices.assert_not_called()
        assert Invoice.objects.count() == 0
        self.company.refresh_from_db()
        assert self.company.ksef_last_fetched_at is None

    def test_task_updates_checkpoint_on_success(
        self, mock_ksef_adapter, mock_ksef_mapper
    ):
        self.company.ksef_last_fetched_at = timezone.make_aware(
            datetime.datetime(2026, 3, 30, 23, 59)
        )
        self.company.save()

        ksef_invoice_data_day2 = {
            "ksefNumber": "KSEF_NUM_1",
            "invoiceNumber": "INV/001",
            "issueDate": "2026-03-31",
            "acquisitionDate": "2026-03-31T10:00:00Z",
            "netAmount": 100.00,
            "grossAmount": 123.00,
            "currency": "PLN",
        }

        mock_ksef_adapter.get_all_purchase_invoices.side_effect = [
            iter([]),
            iter([[ksef_invoice_data_day2]]),
        ]
        mock_ksef_adapter.get_invoice_xml.return_value = "<xml>invoice</xml>"

        with patch("invoices.tasks.timezone.now") as mock_now:
            mock_now.return_value = timezone.make_aware(
                datetime.datetime(2026, 3, 31, 12, 0)
            )
            fetch_purchase_invoices_from_ksef()

        self.company.refresh_from_db()
        assert self.company.ksef_last_fetched_at.date() == datetime.date(2026, 3, 31)
        assert Invoice.objects.count() == 1

    def test_task_does_not_update_checkpoint_on_fetch_failure(self, mock_ksef_adapter):
        self.company.ksef_last_fetched_at = timezone.make_aware(
            datetime.datetime(2026, 3, 30, 23, 59)
        )
        self.company.save()

        mock_ksef_adapter.get_all_purchase_invoices.side_effect = Exception("API Error")

        with patch("invoices.tasks.timezone.now") as mock_now:
            mock_now.return_value = timezone.make_aware(
                datetime.datetime(2026, 3, 31, 12, 0)
            )
            fetch_purchase_invoices_from_ksef()

        self.company.refresh_from_db()
        assert self.company.ksef_last_fetched_at.date() == datetime.date(2026, 3, 30)
        assert Invoice.objects.count() == 0

    def test_task_handles_pagination(self, mock_ksef_adapter, mock_ksef_mapper):
        page1 = [
            {"ksefNumber": f"KSEF_NUM_{i}", "invoiceNumber": f"INV/{i}"}
            for i in range(3)
        ]
        page2 = [
            {"ksefNumber": f"KSEF_NUM_{i}", "invoiceNumber": f"INV/{i}"}
            for i in range(3, 5)
        ]
        mock_ksef_adapter.get_all_purchase_invoices.return_value = iter([page1, page2])
        mock_ksef_adapter.get_invoice_xml.return_value = "<xml>invoice</xml>"

        fetch_purchase_invoices_from_ksef()

        assert Invoice.objects.count() == 5
        assert mock_ksef_adapter.get_invoice_xml.call_count == 5

    def test_task_does_not_update_checkpoint_on_xml_fetch_failure(
        self, mock_ksef_adapter, mock_ksef_mapper
    ):
        self.company.ksef_last_fetched_at = timezone.make_aware(
            datetime.datetime(2026, 4, 10, 23, 59)
        )
        self.company.save()
        ksef_invoice_data = {"ksefNumber": "KSEF_NUM_1", "invoiceNumber": "INV/001"}
        mock_ksef_adapter.get_all_purchase_invoices.return_value = iter(
            [[ksef_invoice_data]]
        )
        mock_ksef_adapter.get_invoice_xml.return_value = None  # Simulate failure

        with patch("invoices.tasks.timezone.now") as mock_now:
            mock_now.return_value = timezone.make_aware(
                datetime.datetime(2026, 4, 11, 12, 0)
            )
            fetch_purchase_invoices_from_ksef()

        self.company.refresh_from_db()
        assert self.company.ksef_last_fetched_at.date() == datetime.date(2026, 4, 10)
        assert Invoice.objects.count() == 0

    def test_task_skips_existing_invoices(self, mock_ksef_adapter, mock_ksef_mapper):
        mock_ksef_mapper[0].return_value.update({"invoice_number": "INV/001"})
        Invoice.objects.create(
            company=self.company,
            invoice_number="INV/001",
            invoice_type=Invoice.INVOICE_PURCHASE,
            sale_date=datetime.date(2026, 4, 1),
            create_date=datetime.date(2026, 4, 1),
            payment_date=datetime.date(2026, 4, 1),
            settlement_date=datetime.date(2026, 4, 1),
            net_amount=100.00,
            gross_amount=123.00,
            currency=self.currency,
        )
        assert Invoice.objects.count() == 1

        ksef_invoice_data = {"ksefNumber": "KSEF_NUM_1", "invoiceNumber": "INV/001"}
        mock_ksef_adapter.get_all_purchase_invoices.return_value = iter(
            [[ksef_invoice_data]]
        )
        mock_ksef_adapter.get_invoice_xml.return_value = "<xml>invoice</xml>"

        fetch_purchase_invoices_from_ksef()

        assert Invoice.objects.count() == 1
        mock_ksef_mapper[0].assert_not_called()

    def test_save_ksef_invoice_creates_invoice_and_items(
        self, mock_ksef_adapter, mock_ksef_mapper
    ):
        ksef_invoice_data = {
            "ksefNumber": "KSEF_NUM_NEW",
            "invoiceNumber": "INV/NEW",
            "currency": "PLN",
        }
        invoice_dict = {
            "invoice_number": "INV/NEW",
            "company": self.company,
            "invoice_type": Invoice.INVOICE_PURCHASE,
            "sale_date": datetime.date(2026, 4, 2),
            "create_date": datetime.date(2026, 4, 2),
            "payment_date": datetime.date(2026, 4, 2),
            "settlement_date": datetime.date(2026, 4, 2),
            "net_amount": 50.00,
            "gross_amount": 61.50,
            "is_recurring": False,
            "is_settled": False,
            "is_paid": False,
            "account_number": "111",
            "payment_method": Invoice.BANK_TRANSFER,
        }
        items_data = [
            {"name": "New Item", "amount": 1, "net_price": 50.00, "vat_rate": 23}
        ]
        mock_ksef_mapper[0].return_value = invoice_dict
        mock_ksef_mapper[1].return_value = items_data
        mock_ksef_adapter.get_invoice_xml.return_value = "<xml>new_invoice</xml>"

        _save_ksef_invoice(ksef_invoice_data, self.company, mock_ksef_adapter)

        assert Invoice.objects.count() == 1
        invoice = Invoice.objects.first()
        assert invoice.invoice_number == "INV/NEW"
        assert invoice.net_amount == 50.00
        assert invoice.gross_amount == 61.50
        assert Item.objects.count() == 1
        item = Item.objects.first()
        assert item.name == "New Item"
        assert item.net_price == 50.00
        assert item.vat.rate == 23

    def test_save_ksef_invoice_handles_xml_fetch_failure(
        self, mock_ksef_adapter, mock_ksef_mapper
    ):
        ksef_invoice_data = {"ksefNumber": "KSEF_NUM_FAIL", "invoiceNumber": "INV/FAIL"}
        mock_ksef_adapter.get_invoice_xml.return_value = None

        with pytest.raises(
            Exception, match="Failed to fetch XML for KSeF invoice KSEF_NUM_FAIL"
        ):
            _save_ksef_invoice(ksef_invoice_data, self.company, mock_ksef_adapter)

        assert Invoice.objects.count() == 0
        assert Item.objects.count() == 0

    def test_save_ksef_invoice_uses_vat_rate_cache(
        self, mock_ksef_adapter, mock_ksef_mapper
    ):
        ksef_invoice_data = {
            "ksefNumber": "KSEF_NUM_CACHE",
            "invoiceNumber": "INV/CACHE",
            "currency": "PLN",
        }
        invoice_dict = {
            "invoice_number": "INV/CACHE",
            "company": self.company,
            "invoice_type": Invoice.INVOICE_PURCHASE,
            "sale_date": datetime.date(2026, 4, 3),
            "create_date": datetime.date(2026, 4, 3),
            "payment_date": datetime.date(2026, 4, 3),
            "settlement_date": datetime.date(2026, 4, 3),
            "net_amount": 150.00,
            "gross_amount": 184.50,
            "is_recurring": False,
            "is_settled": False,
            "is_paid": False,
            "account_number": "222",
            "payment_method": Invoice.BANK_TRANSFER,
        }

        items_data = [
            {"name": "Item 1", "amount": 1, "net_price": 50.00, "vat_rate": 23},
            {"name": "Item 2", "amount": 2, "net_price": 100.00, "vat_rate": 23},
        ]

        mock_ksef_mapper[0].return_value = invoice_dict
        mock_ksef_mapper[1].return_value = items_data
        mock_ksef_adapter.get_invoice_xml.return_value = "<xml>cache_invoice</xml>"

        _save_ksef_invoice(ksef_invoice_data, self.company, mock_ksef_adapter)

        assert Invoice.objects.count() == 1
        assert Item.objects.count() == 2

        items = Item.objects.all()
        assert items[0].vat == items[1].vat
        assert items[0].vat.rate == 23
