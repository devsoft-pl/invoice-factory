from typing import Optional

import requests


class CEIDGAdapter:
    base_url = "https://dane.biznes.gov.pl/api/ceidg/v2/firma"

    def __init__(self, token=None):
        self.token = token

    def _get_company_data(self, nip):
        url = f"{self.base_url}?nip={nip}"

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}",
        }
        response = requests.get(url, headers=headers)

        if not response.status_code == 200:
            return None

        return response.json()

    def is_company_active(self, nip: str) -> Optional[bool]:
        data = self._get_company_data(nip)

        if not data:
            return None

        return data["firma"][0]["status"] == "AKTYWNY"


if __name__ == "__main__":  # pragma: no cover
    import os

    import django

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "base.settings.dev")
    django.setup()

    from django.conf import settings

    adapter = CEIDGAdapter(settings.CEIDG_API_TOKEN)
    status = adapter.is_company_active("example_nip")
    print(f"Status firmy: {status}")
