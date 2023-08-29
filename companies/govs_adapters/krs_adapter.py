import requests


class KrsAdapter:
    base_url = "https://api-krs.ms.gov.pl/api/"

    def _get_company_full_report(self, krs):
        url = f"{self.base_url}krs/OdpisPelny/{krs}"
        params = {"rejestr": "p", "format": "json"}

        response = requests.get(url, params, headers={"Accept": "application/json"})

        if not response.status_code == 200:
            return None

        return response.json()

    def _get_company_data(self, krs):
        url = f"{self.base_url}krs/OdpisAktualny/{krs}?rejestr=p&format=json"

        response = requests.get(url, headers={"Accept": "application/json"})

        if not response.status_code == 200:
            return None

        return response.json()

    def get_nip(self, krs):
        data = self._get_company_data(krs)

        if not data:
            return None

        return data["odpis"]["dane"]["dzial1"]["danePodmiotu"]["identyfikatory"]["nip"]

    def get_regon(self, krs):
        data = self._get_company_data(krs)

        if not data:
            return None

        return data["odpis"]["dane"]["dzial1"]["danePodmiotu"]["identyfikatory"][
            "regon"
        ]


if __name__ == "__main__":  # pragma: no cover
    adapter = KrsAdapter()
    nip = adapter.get_nip("0000029537")
    print(f"NIP firmy: {nip}")

    regon = adapter.get_regon("0000029537")
    print(f"Regon firmy: {regon}")
