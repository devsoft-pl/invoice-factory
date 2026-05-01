import datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from invoices.adapters.ksef_mapper import (
    _parse_date,
    map_ksef_invoice_to_dict,
    map_ksef_invoice_to_items,
    map_ksef_invoice_to_seller_dict,
)
from invoices.models import Invoice


class TestKSeFMapper:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.mock_company = MagicMock(name="CompanyMock")

    @patch("invoices.adapters.ksef_mapper.date")
    def test_parse_date_returns_today_on_empty_value(self, mock_date):
        mock_date.today.return_value = datetime.date(2026, 4, 30)

        assert _parse_date(None) == datetime.date(2026, 4, 30)
        assert _parse_date("") == datetime.date(2026, 4, 30)

    def test_parse_date_parses_issue_date_format(self):
        result = _parse_date("2026-04-01")

        assert result == datetime.date(2026, 4, 1)

    def test_parse_date_parses_acquisition_date_format(self):
        result = _parse_date("2026-04-02T15:30:00Z")

        assert result == datetime.date(2026, 4, 2)

    def test_map_ksef_invoice_to_seller_dict_empty(self):
        ksef_invoice = {}
        result = map_ksef_invoice_to_seller_dict(ksef_invoice)

        assert result == {"nip": None, "name": None}

    def test_map_ksef_invoice_to_seller_dict_populated(self):
        ksef_invoice = {
            "seller": {"nip": "1234567890", "name": "Sprzedawca Sp. z o.o."}
        }
        result = map_ksef_invoice_to_seller_dict(ksef_invoice)

        assert result == {"nip": "1234567890", "name": "Sprzedawca Sp. z o.o."}

    @patch("invoices.adapters.ksef_mapper.map_ksef_xml_to_items")
    def test_map_ksef_invoice_to_items(self, mock_xml_to_items):
        mock_xml_to_items.return_value = [{"name": "Usługa X", "amount": 1}]

        result = map_ksef_invoice_to_items("<xml>items</xml>")

        assert result == [{"name": "Usługa X", "amount": 1}]
        mock_xml_to_items.assert_called_once_with("<xml>items</xml>")

    def test_map_ksef_invoice_to_dict_without_xml(self):
        ksef_invoice = {
            "invoiceNumber": "FA/2026/04/01",
            "issueDate": "2026-04-01",
            "acquisitionDate": "2026-04-02T12:00:00Z",
            "netAmount": 100.50,
            "grossAmount": 123.61,
        }

        result = map_ksef_invoice_to_dict(ksef_invoice, self.mock_company)

        assert result["invoice_number"] == "FA/2026/04/01"
        assert result["invoice_type"] == Invoice.INVOICE_PURCHASE
        assert result["company"] == self.mock_company  # ZMIANA: self.mock_company
        assert result["sale_date"] == datetime.date(2026, 4, 1)
        assert result["create_date"] == datetime.date(2026, 4, 2)
        assert result["account_number"] is None
        assert result["payment_method"] is None
        assert result["net_amount"] == Decimal("100.50")
        assert result["gross_amount"] == Decimal("123.61")
        assert result["is_recurring"] is False
        assert result["is_settled"] is False
        assert result["is_paid"] is False

    @patch("invoices.adapters.ksef_mapper.map_ksef_xml_to_payment")
    def test_map_ksef_invoice_to_dict_with_xml(self, mock_xml_to_payment):
        ksef_invoice = {
            "invoiceNumber": "FA/2026/04/01",
            "netAmount": None,
        }
        mock_xml_to_payment.return_value = {
            "account_number": "11112222333344445555666677",
            "payment_method": Invoice.BANK_TRANSFER,
        }

        result = map_ksef_invoice_to_dict(
            ksef_invoice, self.mock_company, xml="<FA3>...</FA3>"
        )

        assert result["account_number"] == "11112222333344445555666677"
        assert result["payment_method"] == Invoice.BANK_TRANSFER
        assert result["net_amount"] == Decimal("0")
        mock_xml_to_payment.assert_called_once_with("<FA3>...</FA3>")
