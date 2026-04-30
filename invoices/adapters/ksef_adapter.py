import base64
import logging
import time
from datetime import date, datetime
from datetime import time as datetime_time
from typing import Any, Dict, Iterator, List, Optional

import requests
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from django.conf import settings
from django.utils import timezone

from base.settings.common import KSEF_API_URL_TEST

logger = logging.getLogger(__name__)

DEFAULT_PAGE_SIZE = 100
AUTH_POLL_MAX_RETRIES = 10
AUTH_POLL_INTERVAL = 1
DEFAULT_TIMEOUT = 15

KSEF_AUTH_STATUS_OK = 200
KSEF_AUTH_STATUS_FAILED = 400


class KSeFAdapter:
    def __init__(self, token: str, nip: str) -> None:
        self.token = token
        self.nip = nip
        self.base_url = (
            settings.KSEF_API_URL_TEST
            if settings.KSEF_IS_TEST
            else settings.KSEF_API_URL_PRODUCTION
        )
        self.session_token: Optional[str] = None
        self.client = requests.Session()

    # --- Wsparcie dla Context Managera (blok "with") ---
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

    def _get_headers(self) -> Dict[str, str]:
        if not self.session_token:
            raise ValueError(
                "KSeF adapter is not authenticated. Call authenticate() first."
            )
        return {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.session_token}",
        }

    # --- NOWA UNIWERSALNA METODA DO ZAPYTAŃ ---
    def _request(
        self, method: str, url: str, error_msg: str = "KSeF request failed", **kwargs
    ) -> Optional[requests.Response]:
        """Ujednolicona metoda do odpytywania API z wbudowaną obsługą wyjątków sieciowych."""
        kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
        try:
            response = self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.error("%s: %s", error_msg, e)
            return None

    def _get_public_key(self) -> Optional[str]:
        """Fetch the current KSeF public key used to encrypt the token."""
        url = f"{self.base_url}/api/v2/security/public-key-certificates"
        response = self._request(
            "GET",
            url,
            error_msg="KSeF failed to get public key",
            headers={"Accept": "application/json"},
        )
        if not response:
            return None

        for cert in response.json():
            if "KsefTokenEncryption" in cert.get("usage", []):
                return cert["certificate"]
        return None

    def _encrypt_token(self, public_key_b64: str, timestamp_ms: int) -> str:
        """Encrypt '{token}|{timestampMs}' with the RSA-OAEP SHA-256 public key."""
        cert_der = base64.b64decode(public_key_b64)
        cert = x509.load_der_x509_certificate(cert_der)
        public_key = cert.public_key()

        payload = f"{self.token}|{timestamp_ms}".encode()

        encrypted = public_key.encrypt(
            payload,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        return base64.b64encode(encrypted).decode()

    def _get_challenge(self) -> Optional[Dict[str, Any]]:
        """Request an authentication challenge from KSeF."""
        url = f"{self.base_url}/api/v2/auth/challenge"
        response = self._request(
            "POST",
            url,
            error_msg="KSeF failed to get challenge",
            headers={"Accept": "application/json"},
        )
        return response.json() if response else None

    def _poll_for_auth_status(
        self, reference_number: str, authentication_token: str
    ) -> bool:
        """Poll KSeF for the status of an asynchronous authentication operation."""
        status_url = f"{self.base_url}/api/v2/auth/{reference_number}"
        auth_headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {authentication_token}",
        }

        for _ in range(AUTH_POLL_MAX_RETRIES):
            response = self._request(
                "GET",
                status_url,
                error_msg="KSeF auth status failed",
                headers=auth_headers,
            )
            if not response:
                return False

            status_code = response.json()["status"]["code"]
            if status_code == KSEF_AUTH_STATUS_OK:
                return True
            if status_code == KSEF_AUTH_STATUS_FAILED:
                logger.error("KSeF auth failed: %s", response.json()["status"])
                return False

            logger.debug("KSeF auth in progress (status=%s), retrying...", status_code)
            time.sleep(AUTH_POLL_INTERVAL)

        logger.error("KSeF auth timed out")
        return False

    def authenticate(self) -> bool:
        """Run the full token authentication flow and store the session token."""
        public_key_b64 = self._get_public_key()
        if not public_key_b64:
            return False

        challenge_data = self._get_challenge()
        if not challenge_data:
            return False

        encrypted_token = self._encrypt_token(
            public_key_b64, challenge_data["timestampMs"]
        )

        url = f"{self.base_url}/api/v2/auth/ksef-token"
        body = {
            "challenge": challenge_data["challenge"],
            "contextIdentifier": {"type": "Nip", "value": self.nip},
            "encryptedToken": encrypted_token,
        }

        logger.debug("KSeF auth request: POST %s", url)
        response = self._request(
            "POST",
            url,
            error_msg="KSeF auth failed",
            json=body,
            headers={"Accept": "application/json"},
        )
        if not response:
            return False

        data = response.json()
        reference_number = data["referenceNumber"]
        authentication_token = data["authenticationToken"]["token"]

        if not self._poll_for_auth_status(reference_number, authentication_token):
            return False

        redeem_url = f"{self.base_url}/api/v2/auth/token/redeem"
        auth_headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {authentication_token}",
        }

        redeem_response = self._request(
            "POST", redeem_url, error_msg="KSeF redeem failed", headers=auth_headers
        )
        if not redeem_response:
            return False

        redeem_data = redeem_response.json()
        self.session_token = redeem_data["accessToken"]["token"]
        logger.debug(
            "KSeF access token valid until: %s",
            redeem_data["accessToken"]["validUntil"],
        )
        return True

    def get_purchase_invoices(
        self,
        date_from: date,
        date_to: date,
        page_size: int = DEFAULT_PAGE_SIZE,
        page_offset: int = 0,
    ) -> Optional[Dict[str, Any]]:
        """Fetch a single page of purchase invoices (company is the buyer)."""
        url = f"{self.base_url}/api/v2/invoices/query/metadata"
        params = {"pageSize": page_size, "pageOffset": page_offset}

        naive_dt_from = datetime.combine(date_from, datetime_time.min)
        naive_dt_to = datetime.combine(date_to, datetime_time(23, 59, 59))
        dt_from = timezone.make_aware(naive_dt_from)
        dt_to = timezone.make_aware(naive_dt_to)

        body = {
            "subjectType": "Subject2",
            "dateRange": {
                "dateType": "Issue",
                "from": dt_from.isoformat(),
                "to": dt_to.isoformat(),
            },
        }
        logger.debug("KSeF request: POST %s body=%s", url, body)

        response = self._request(
            "POST",
            url,
            error_msg="KSeF error",
            params=params,
            json=body,
            headers=self._get_headers(),
        )
        return response.json() if response else None

    def get_invoice_xml(self, ksef_number: str) -> Optional[str]:
        """Fetch the full FA(3) XML of an invoice by its KSeF number."""
        url = f"{self.base_url}/api/v2/invoices/ksef/{ksef_number}"
        response = self._request(
            "GET",
            url,
            error_msg="KSeF invoice XML error",
            headers={**self._get_headers(), "Accept": "application/xml"},
        )
        return response.text if response else None

    def get_all_purchase_invoices(
        self, date_from: date, date_to: date
    ) -> Iterator[List[Dict[str, Any]]]:
        """Generator yielding pages of invoice metadata, DEFAULT_PAGE_SIZE per page."""
        page_offset = 0

        while True:
            data = self.get_purchase_invoices(
                date_from, date_to, DEFAULT_PAGE_SIZE, page_offset
            )
            if not data:
                return
            yield data.get("invoices", [])
            if not data.get("hasMore"):
                return
            page_offset += DEFAULT_PAGE_SIZE


if __name__ == "__main__":  # pragma: no cover
    import logging
    import os
    from datetime import date

    logging.basicConfig(level=logging.DEBUG)

    if not settings.configured:
        settings.configure(
            KSEF_API_URL_TEST=KSEF_API_URL_TEST,
            KSEF_API_URL_PRODUCTION="https://ksef.mf.gov.pl",
            KSEF_IS_TEST=True,
            TIME_ZONE="Europe/Warsaw",
            USE_TZ=True,
        )

    token = os.environ.get("KSEF_TOKEN", "test_token")
    nip = os.environ.get("KSEF_NIP", "1111111111")

    with KSeFAdapter(token, nip) as adapter:
        if not adapter.authenticate():
            print("Authentication failed")
            raise SystemExit(1)

        first_invoice = None
        for page in adapter.get_all_purchase_invoices(
            date(2026, 4, 1), date(2026, 4, 14)
        ):
            print(f"Page: {len(page)} invoices")
            for invoice in page:
                print(f"  {invoice.get('ksefNumber')} — {invoice.get('invoiceNumber')}")
                if first_invoice is None:
                    first_invoice = invoice

        if first_invoice:
            print(f"\nFetching XML for first invoice: {first_invoice['ksefNumber']}")
            xml = adapter.get_invoice_xml(first_invoice["ksefNumber"])
            print(xml)
