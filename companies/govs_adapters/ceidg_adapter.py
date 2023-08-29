import requests


class CEIDGAdapter:
    base_url = "https://dane.biznes.gov.pl/api/"

    def _get_company_data(self, nip):
        url = f"{self.base_url}ceidg/v2/firmy?nip={nip}"
        response = requests.get(url, headers={"Accept": "application/json"})

        if not response.status_code == 200:
            return None

        return response.json()

    def get_status(self, nip):
        data = self._get_company_data(nip)

        if not data:
            return None

        return "w oczekiwaniu na api i tocken"


if __name__ == "__main__":  # pragma: no cover
    adapter = CEIDGAdapter()
    status = adapter.get_status("6711573118")
    print(f"Status firmy: {status}")
