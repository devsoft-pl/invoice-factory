import base64
from unittest.mock import MagicMock, patch

import pytest
import requests

from invoices.adapters.ksef_adapter import (
    DEFAULT_PAGE_SIZE,
    KSEF_AUTH_STATUS_FAILED,
    KSEF_AUTH_STATUS_OK,
    KSeFAdapter,
)


class TestKSeFAdapter:
    @pytest.fixture(autouse=True)
    def set_up(self, settings) -> None:
        settings.KSEF_IS_TEST = True
        settings.KSEF_API_URL_TEST = "https://test-ksef.api"
        settings.KSEF_API_URL_PRODUCTION = "https://prod-ksef.api"

        self.adapter = KSeFAdapter(token="secret_token", nip="1234567890")

    def test_init_uses_correct_url_based_on_settings(self, settings):
        settings.KSEF_IS_TEST = True
        adapter_test = KSeFAdapter("token", "nip")

        assert adapter_test.base_url == settings.KSEF_API_URL_TEST

        settings.KSEF_IS_TEST = False
        adapter_prod = KSeFAdapter("token", "nip")
        assert adapter_prod.base_url == settings.KSEF_API_URL_PRODUCTION

    def test_get_headers_success(self):
        self.adapter.session_token = "fake_session_token"

        headers = self.adapter._get_headers()

        assert headers["Accept"] == "application/json"
        assert headers["Authorization"] == "Bearer fake_session_token"

    def test_get_headers_raises_value_error(self):
        self.adapter.session_token = None

        with pytest.raises(ValueError, match="KSeF adapter is not authenticated"):
            self.adapter._get_headers()

    @patch("requests.Session.request")
    def test_get_public_key_success(self, mock_request):
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"usage": ["OtherUsage"], "certificate": "wrong_cert"},
            {"usage": ["KsefTokenEncryption"], "certificate": "correct_cert"},
        ]
        mock_request.return_value = mock_response

        cert = self.adapter._get_public_key()

        assert cert == "correct_cert"
        mock_request.assert_called_once_with(
            "GET",
            f"{self.adapter.base_url}/api/v2/security/public-key-certificates",
            headers={"Accept": "application/json"},
            timeout=15,
        )

    @patch("requests.Session.request")
    def test_get_public_key_returns_none_when_no_valid_cert_found(self, mock_request):
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"usage": ["Signing"], "certificate": "cert1"},
        ]
        mock_request.return_value = mock_response

        cert = self.adapter._get_public_key()
        assert cert is None

    @patch("requests.Session.request")
    def test_get_public_key_request_exception(self, mock_request):
        mock_request.side_effect = requests.RequestException("API down")
        cert = self.adapter._get_public_key()

        assert cert is None

    @patch("invoices.adapters.ksef_adapter.x509.load_der_x509_certificate")
    @patch("invoices.adapters.ksef_adapter.base64.b64decode")
    def test_encrypt_token(self, mock_b64decode, mock_load_cert):
        mock_cert = MagicMock()
        mock_public_key = MagicMock()
        mock_public_key.encrypt.return_value = b"encrypted_payload"
        mock_cert.public_key.return_value = mock_public_key
        mock_load_cert.return_value = mock_cert
        mock_b64decode.return_value = b"der_cert"

        result = self.adapter._encrypt_token("base64_pub_key", 123456789)

        mock_public_key.encrypt.assert_called_once()
        assert result == base64.b64encode(b"encrypted_payload").decode()

    @patch("requests.Session.request")
    def test_get_challenge_success(self, mock_request):
        mock_response = MagicMock()
        mock_response.json.return_value = {"challenge": "xyz", "timestampMs": 123}
        mock_request.return_value = mock_response

        result = self.adapter._get_challenge()

        assert result == {"challenge": "xyz", "timestampMs": 123}

    @patch("requests.Session.request")
    def test_get_challenge_request_exception(self, mock_request):
        mock_request.side_effect = requests.RequestException("API error")

        assert self.adapter._get_challenge() is None

    @patch("requests.Session.request")
    def test_poll_for_auth_status_success_on_first_try(self, mock_request):
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": {"code": KSEF_AUTH_STATUS_OK}}
        mock_request.return_value = mock_response

        result = self.adapter._poll_for_auth_status("ref123", "auth_token")

        assert result is True

    @patch("requests.Session.request")
    def test_poll_for_auth_status_returns_false_on_auth_failed_status(
        self, mock_request
    ):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": {
                "code": KSEF_AUTH_STATUS_FAILED,
                "description": "Invalid credentials",
            }
        }
        mock_request.return_value = mock_response

        result = self.adapter._poll_for_auth_status("ref123", "auth_token")

        assert result is False

    @patch("invoices.adapters.ksef_adapter.time.sleep")
    @patch("requests.Session.request")
    def test_poll_for_auth_status_retries_and_fails(self, mock_request, mock_sleep):
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": {"code": 315}}
        mock_request.return_value = mock_response

        result = self.adapter._poll_for_auth_status("ref123", "auth_token")

        assert result is False
        assert mock_request.call_count == 10
        assert mock_sleep.call_count == 10

    @patch("requests.Session.request")
    def test_poll_for_auth_status_returns_false_on_request_exception(
        self, mock_request
    ):
        mock_request.side_effect = requests.RequestException("Network timeout")

        result = self.adapter._poll_for_auth_status("ref123", "auth_token")

        assert result is False

    @patch.object(KSeFAdapter, "_get_public_key")
    @patch.object(KSeFAdapter, "_get_challenge")
    @patch.object(KSeFAdapter, "_encrypt_token")
    @patch.object(KSeFAdapter, "_poll_for_auth_status")
    @patch("requests.Session.request")
    def test_authenticate_success(
        self, mock_request, mock_poll, mock_encrypt, mock_challenge, mock_pub_key
    ):
        mock_pub_key.return_value = "pub_key"
        mock_challenge.return_value = {"challenge": "chal123", "timestampMs": 123}
        mock_encrypt.return_value = "encrypted_token"
        mock_poll.return_value = True

        mock_auth_resp = MagicMock()
        mock_auth_resp.json.return_value = {
            "referenceNumber": "ref123",
            "authenticationToken": {"token": "auth_tok"},
        }

        mock_redeem_resp = MagicMock()
        mock_redeem_resp.json.return_value = {
            "accessToken": {"token": "session_tok", "validUntil": "2026-05-01"}
        }

        mock_request.side_effect = [mock_auth_resp, mock_redeem_resp]

        result = self.adapter.authenticate()

        assert result is True
        assert self.adapter.session_token == "session_tok"
        assert mock_request.call_count == 2

    @patch.object(KSeFAdapter, "_get_public_key")
    @patch.object(KSeFAdapter, "_get_challenge")
    def test_authenticate_fails_when_no_challenge_data(
        self, mock_challenge, mock_pub_key
    ):
        mock_pub_key.return_value = "pub_key"
        mock_challenge.return_value = None

        assert self.adapter.authenticate() is False

    @patch.object(KSeFAdapter, "_get_public_key")
    @patch.object(KSeFAdapter, "_get_challenge")
    @patch.object(KSeFAdapter, "_encrypt_token")
    @patch("requests.Session.request")
    def test_authenticate_fails_on_auth_post_request_exception(
        self, mock_request, mock_encrypt, mock_challenge, mock_pub_key
    ):
        mock_pub_key.return_value = "pub_key"
        mock_challenge.return_value = {"challenge": "chal123", "timestampMs": 123}
        mock_encrypt.return_value = "encrypted_token"
        mock_request.side_effect = requests.RequestException("Auth POST failed")

        assert self.adapter.authenticate() is False

    @patch.object(KSeFAdapter, "_get_public_key")
    @patch.object(KSeFAdapter, "_get_challenge")
    @patch.object(KSeFAdapter, "_encrypt_token")
    @patch.object(KSeFAdapter, "_poll_for_auth_status")
    @patch("requests.Session.request")
    def test_authenticate_fails_when_poll_returns_false(
        self, mock_request, mock_poll, mock_encrypt, mock_challenge, mock_pub_key
    ):
        mock_pub_key.return_value = "pub_key"
        mock_challenge.return_value = {"challenge": "chal123", "timestampMs": 123}
        mock_encrypt.return_value = "encrypted_token"

        mock_auth_resp = MagicMock()
        mock_auth_resp.json.return_value = {
            "referenceNumber": "ref123",
            "authenticationToken": {"token": "auth_tok"},
        }
        mock_request.return_value = mock_auth_resp
        mock_poll.return_value = False

        assert self.adapter.authenticate() is False

    @patch.object(KSeFAdapter, "_get_public_key")
    @patch.object(KSeFAdapter, "_get_challenge")
    @patch.object(KSeFAdapter, "_encrypt_token")
    @patch.object(KSeFAdapter, "_poll_for_auth_status")
    @patch("requests.Session.request")
    def test_authenticate_fails_on_redeem_post_request_exception(
        self, mock_request, mock_poll, mock_encrypt, mock_challenge, mock_pub_key
    ):
        mock_pub_key.return_value = "pub_key"
        mock_challenge.return_value = {"challenge": "chal123", "timestampMs": 123}
        mock_encrypt.return_value = "encrypted_token"
        mock_poll.return_value = True

        mock_auth_resp = MagicMock()
        mock_auth_resp.json.return_value = {
            "referenceNumber": "ref123",
            "authenticationToken": {"token": "auth_tok"},
        }

        mock_request.side_effect = [
            mock_auth_resp,
            requests.RequestException("Redeem POST failed"),
        ]

        assert self.adapter.authenticate() is False

    @patch("requests.Session.request")
    def test_get_purchase_invoices_success(self, mock_request):
        self.adapter.session_token = "token"
        mock_response = MagicMock()
        mock_response.json.return_value = {"invoices": [{"id": 1}], "hasMore": False}
        mock_request.return_value = mock_response

        from datetime import date

        result = self.adapter.get_purchase_invoices(date(2026, 4, 1), date(2026, 4, 30))

        assert result == {"invoices": [{"id": 1}], "hasMore": False}
        called_kwargs = mock_request.call_args[1]
        assert "2026-04-01T00:00:00" in called_kwargs["json"]["dateRange"]["from"]

    @patch("requests.Session.request")
    def test_get_purchase_invoices_request_exception(self, mock_request):
        self.adapter.session_token = "token"
        mock_request.side_effect = requests.RequestException("API connection timeout")

        from datetime import date

        result = self.adapter.get_purchase_invoices(date(2026, 4, 1), date(2026, 4, 30))
        assert result is None

    @patch("requests.Session.request")
    def test_get_invoice_xml_success(self, mock_request):
        self.adapter.session_token = "token"
        mock_response = MagicMock()
        mock_response.text = "<xml>Faktura</xml>"
        mock_request.return_value = mock_response

        result = self.adapter.get_invoice_xml("KSEF_123")

        assert result == "<xml>Faktura</xml>"
        called_headers = mock_request.call_args[1]["headers"]
        assert called_headers["Accept"] == "application/xml"

    @patch("requests.Session.request")
    def test_get_invoice_xml_request_exception(self, mock_request):
        self.adapter.session_token = "token"
        mock_request.side_effect = requests.RequestException("Failed to download XML")
        result = self.adapter.get_invoice_xml("KSEF_123")
        assert result is None

    @patch.object(KSeFAdapter, "get_purchase_invoices")
    def test_get_all_purchase_invoices_pagination(self, mock_get_purchase):
        page_1 = {"invoices": [{"id": 1}, {"id": 2}], "hasMore": True}
        page_2 = {"invoices": [{"id": 3}], "hasMore": False}

        mock_get_purchase.side_effect = [page_1, page_2]

        from datetime import date

        pages = list(
            self.adapter.get_all_purchase_invoices(date(2026, 4, 1), date(2026, 4, 30))
        )

        assert len(pages) == 2
        assert pages[0] == [{"id": 1}, {"id": 2}]
        assert pages[1] == [{"id": 3}]
        assert mock_get_purchase.call_args_list[0][0][3] == 0
        assert mock_get_purchase.call_args_list[1][0][3] == DEFAULT_PAGE_SIZE

    def test_context_manager(self):
        from invoices.adapters.ksef_adapter import KSeFAdapter

        with patch("requests.Session.close") as mock_close:
            with KSeFAdapter("token", "nip") as adapter:
                assert isinstance(adapter, KSeFAdapter)
            mock_close.assert_called_once()

    @patch.object(KSeFAdapter, "_get_public_key")
    def test_authenticate_fails_when_no_public_key(self, mock_pub_key):
        mock_pub_key.return_value = None

        assert self.adapter.authenticate() is False

    @patch.object(KSeFAdapter, "get_purchase_invoices")
    def test_get_all_purchase_invoices_returns_when_no_data(self, mock_get_purchase):
        mock_get_purchase.return_value = None

        from datetime import date

        pages = list(
            self.adapter.get_all_purchase_invoices(date(2026, 4, 1), date(2026, 4, 30))
        )

        assert pages == []
        mock_get_purchase.assert_called_once()
