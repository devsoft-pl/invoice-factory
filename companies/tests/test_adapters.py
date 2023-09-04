from unittest.mock import Mock, patch

import pytest

from companies.govs_adapters.ceidg_adapter import CEIDGAdapter
from companies.govs_adapters.krs_adapter import KrsAdapter


class TestCEIDGAdapter:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        token = "Bearer 123456789"
        self.adapter = CEIDGAdapter(token=token)

    @pytest.mark.parametrize(
        "status, value",
        [
            ["AKTYWNY", True],
            ["ZAWIESZONY", False],
            ["ZAMKNIĘTY", False],
        ],
    )
    @patch("companies.govs_adapters.ceidg_adapter.CEIDGAdapter._get_company_data")
    def test_checks_company_status(self, _get_company_data_mock, status, value):
        company_data = {
            "firma": [
                {
                    "id": "1",
                    "nazwa": "Testowa Firma",
                    "adresDzialalnosci": {
                        "ulica": "Testowa ulica",
                        "budynek": "1",
                        "miasto": "Testowe miasto",
                        "kraj": "PL",
                        "kod": "00-001",
                    },
                    "adresKorespondencyjny": {
                        "ulica": "Testowa ulica",
                        "budynek": "1",
                        "miasto": "Testowe miasto",
                        "kraj": "PL",
                        "kod": "00-001",
                    },
                    "wlasciciel": {
                        "imie": "Testowe imie",
                        "nazwisko": "Testowe nazwisko",
                        "nip": "123456789",
                        "regon": "111111111",
                    },
                    "obywatelstwa": [{"symbol": "PL", "kraj": "Polska"}],
                    "pkd": ["Testowe pkd"],
                    "dataRozpoczecia": "2022-07-11",
                    "status": status,
                }
            ],
            "properties": {
                "dc:title": "firma",
            },
        }
        _get_company_data_mock.return_value = company_data

        assert self.adapter.is_company_active("123456789") == value

    @patch("companies.govs_adapters.ceidg_adapter.CEIDGAdapter._get_company_data")
    def test_returns_none_when_not_data(self, _get_company_data_mock):
        _get_company_data_mock.return_value = {}

        assert not self.adapter.is_company_active("123456789")

    @patch("companies.govs_adapters.ceidg_adapter.requests.get")
    def test_get_company_data_not_returns_status_code_200(self, requests_get_mock):
        requests_get_mock.return_value = Mock(status_code=400)

        assert not self.adapter.is_company_active("123456789")


class TestKrsAdapter:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.adapter = KrsAdapter()
        self.krs = "0000012345"
        self.company_data = {
            "odpis": {
                "rodzaj": "Aktualny",
                "naglowekA": {"numerKRS": "0000012345", "stanPozycji": 1},
                "dane": {
                    "dzial1": {
                        "danePodmiotu": {
                            "identyfikatory": {"regon": "...", "nip": "123456789"}
                        }
                    }
                },
            }
        }

    @patch("companies.govs_adapters.krs_adapter.requests.get")
    def test_get_full_company_data_returns_status_code_200(self, requests_get_mock):
        requests_get_mock.return_value = Mock(status_code=200)

        assert self.adapter._get_company_full_report(self.krs)

    @patch("companies.govs_adapters.krs_adapter.requests.get")
    def test_get_full_company_data_not_returns_status_code_200(self, requests_get_mock):
        requests_get_mock.return_value = Mock(status_code=400)

        assert not self.adapter._get_company_full_report(self.krs)

    @patch("companies.govs_adapters.krs_adapter.KrsAdapter._get_company_data")
    def test_returns_company_nip(self, _get_company_data_mock):
        _get_company_data_mock.return_value = self.company_data

        assert (
            self.adapter.get_nip(self.krs)
            == self.company_data["odpis"]["dane"]["dzial1"]["danePodmiotu"][
                "identyfikatory"
            ]["nip"]
        )

    @patch("companies.govs_adapters.krs_adapter.KrsAdapter._get_company_data")
    def test_returns_company_regon(self, _get_company_data_mock):
        _get_company_data_mock.return_value = self.company_data

        assert (
            self.adapter.get_regon(self.krs)
            == self.company_data["odpis"]["dane"]["dzial1"]["danePodmiotu"][
                "identyfikatory"
            ]["regon"]
        )

    @patch("companies.govs_adapters.krs_adapter.KrsAdapter._get_company_data")
    def test_returns_none_if_not_have_data_when_want_nip(self, _get_company_data_mock):
        _get_company_data_mock.return_value = {}

        assert not self.adapter.get_nip(self.krs)

    @patch("companies.govs_adapters.krs_adapter.KrsAdapter._get_company_data")
    def test_returns_none_if_not_have_data_when_want_regon(
        self, _get_company_data_mock
    ):
        _get_company_data_mock.return_value = {}

        assert not self.adapter.get_regon(self.krs)

    @patch("companies.govs_adapters.krs_adapter.requests.get")
    def test_get_company_data_not_returns_status_code_200(self, requests_get_mock):
        requests_get_mock.return_value = Mock(status_code=400)

        assert not self.adapter.get_nip(self.krs)
