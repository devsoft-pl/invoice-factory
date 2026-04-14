import base64
import logging
import time

import requests
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

logger = logging.getLogger(__name__)

KSEF_API_URL_TEST = "https://api-test.ksef.mf.gov.pl"
KSEF_API_URL_PRODUCTION = "https://api.ksef.mf.gov.pl"

DEFAULT_PAGE_SIZE = 100
AUTH_POLL_MAX_RETRIES = 10
AUTH_POLL_INTERVAL = 1  # seconds

KSEF_AUTH_STATUS_OK = 200
KSEF_AUTH_STATUS_FAILED = 400


class KSeFAdapter:
    def __init__(self, token, nip, base_url=KSEF_API_URL_TEST):
        self.token = token
        self.nip = nip
        self.base_url = base_url
        self.session_token = None

    def _get_headers(self):
        return {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.session_token}",
        }

    def _get_public_key(self):
        """Fetch the current KSeF public key used to encrypt the token."""
        url = f"{self.base_url}/api/v2/security/public-key-certificates"
        response = requests.get(url, headers={"Accept": "application/json"})

        logger.debug("KSeF public key response: status=%s", response.status_code)

        if response.status_code != 200:
            logger.error(
                "KSeF failed to get public key: status=%s body=%s",
                response.status_code,
                response.text,
            )
            return None

        certs = response.json()
        for cert in certs:
            if "KsefTokenEncryption" in cert.get("usage", []):
                return cert["certificate"]

        return None

    def _encrypt_token(self, public_key_b64, timestamp_ms):
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

    def _get_challenge(self):
        """Request an authentication challenge from KSeF."""
        url = f"{self.base_url}/api/v2/auth/challenge"
        response = requests.post(url, headers={"Accept": "application/json"})

        logger.debug(
            "KSeF challenge response: status=%s body=%s",
            response.status_code,
            response.text,
        )

        if response.status_code != 200:
            logger.error(
                "KSeF failed to get challenge: status=%s body=%s",
                response.status_code,
                response.text,
            )
            return None

        return response.json()

    def authenticate(self):
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
            "contextIdentifier": {
                "type": "Nip",
                "value": self.nip,
            },
            "encryptedToken": encrypted_token,
        }

        logger.debug("KSeF auth request: POST %s", url)
        response = requests.post(url, json=body, headers={"Accept": "application/json"})
        logger.debug(
            "KSeF auth response: status=%s body=%s", response.status_code, response.text
        )

        if response.status_code not in (200, 202):
            logger.error(
                "KSeF auth failed: status=%s body=%s",
                response.status_code,
                response.text,
            )
            return False

        data = response.json()
        reference_number = data["referenceNumber"]
        authentication_token = data["authenticationToken"]["token"]

        # poll authentication status — the operation is asynchronous
        status_url = f"{self.base_url}/api/v2/auth/{reference_number}"
        auth_headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {authentication_token}",
        }

        for _ in range(AUTH_POLL_MAX_RETRIES):
            status_response = requests.get(status_url, headers=auth_headers)
            logger.debug(
                "KSeF auth status: status=%s body=%s",
                status_response.status_code,
                status_response.text,
            )

            if status_response.status_code != 200:
                logger.error(
                    "KSeF auth status failed: status=%s", status_response.status_code
                )
                return False

            status_code = status_response.json()["status"]["code"]
            if status_code == KSEF_AUTH_STATUS_OK:
                break
            if status_code == KSEF_AUTH_STATUS_FAILED:
                logger.error("KSeF auth failed: %s", status_response.json()["status"])
                return False

            logger.debug("KSeF auth in progress (status=%s), retrying...", status_code)
            time.sleep(AUTH_POLL_INTERVAL)
        else:
            logger.error("KSeF auth timed out")
            return False

        redeem_url = f"{self.base_url}/api/v2/auth/token/redeem"
        redeem_response = requests.post(redeem_url, headers=auth_headers)
        logger.debug(
            "KSeF redeem response: status=%s body=%s",
            redeem_response.status_code,
            redeem_response.text,
        )

        if redeem_response.status_code != 200:
            logger.error(
                "KSeF redeem failed: status=%s body=%s",
                redeem_response.status_code,
                redeem_response.text,
            )
            return False

        redeem_data = redeem_response.json()
        self.session_token = redeem_data["accessToken"]["token"]
        logger.debug(
            "KSeF access token valid until: %s",
            redeem_data["accessToken"]["validUntil"],
        )
        return True

    def get_purchase_invoices(
        self, date_from, date_to, page_size=DEFAULT_PAGE_SIZE, page_offset=0
    ):
        """Fetch a single page of purchase invoices (company is the buyer)."""
        url = f"{self.base_url}/api/v2/invoices/query/metadata"
        body = {
            "pageSize": page_size,
            "pageOffset": page_offset,
            "subjectType": "Subject2",
            "dateRange": {
                "dateType": "Issue",
                "from": f"{date_from}T00:00:00+00:00",
                "to": f"{date_to}T23:59:59+00:00",
            },
        }
        logger.debug("KSeF request: POST %s body=%s", url, body)

        response = requests.post(url, json=body, headers=self._get_headers())
        logger.debug(
            "KSeF response: status=%s body=%s", response.status_code, response.text
        )

        if response.status_code != 200:
            logger.error(
                "KSeF error: status=%s body=%s", response.status_code, response.text
            )
            return None

        return response.json()

    def get_invoice_xml(self, ksef_number):
        """Fetch the full FA(3) XML of an invoice by its KSeF number."""
        url = f"{self.base_url}/api/v2/invoices/ksef/{ksef_number}"
        response = requests.get(
            url, headers={**self._get_headers(), "Accept": "application/xml"}
        )
        logger.debug(
            "KSeF invoice XML: status=%s ksefNumber=%s",
            response.status_code,
            ksef_number,
        )

        if response.status_code != 200:
            logger.error(
                "KSeF invoice XML error: status=%s body=%s",
                response.status_code,
                response.text,
            )
            return None

        return response.text

    def get_all_purchase_invoices(self, date_from, date_to):
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
    import os
    from datetime import date

    logging.basicConfig(level=logging.DEBUG)

    token = os.environ["KSEF_TOKEN"]
    nip = os.environ["KSEF_NIP"]
    base_url = os.environ.get("KSEF_API_URL", KSEF_API_URL_TEST)

    adapter = KSeFAdapter(token, nip, base_url)

    if not adapter.authenticate():
        print("Authentication failed")
        raise SystemExit(1)

    first_invoice = None
    for page in adapter.get_all_purchase_invoices(date(2026, 4, 1), date(2026, 4, 14)):
        print(f"Page: {len(page)} invoices")
        for invoice in page:
            print(f"  {invoice.get('ksefNumber')} — {invoice.get('invoiceNumber')}")
            if first_invoice is None:
                first_invoice = invoice

    if first_invoice:
        print(f"\nFetching XML for first invoice: {first_invoice['ksefNumber']}")
        xml = adapter.get_invoice_xml(first_invoice["ksefNumber"])
        print(xml)
