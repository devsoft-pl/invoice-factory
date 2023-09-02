from unittest.mock import call, patch

import pytest

from companies.factories import CompanyFactory
from companies.tasks import (check_company_status,
                             check_company_status_for_all_contractors)
from users.factories import UserFactory


@pytest.mark.django_db
class TestCompaniesStatusTasks:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.user = UserFactory.create()
        self.company = CompanyFactory.create(
            user=self.user, is_my_company=False, nip="111111111"
        )
        self.active_status = "AKTYWNY"

    @patch("companies.tasks.check_company_status.apply_async")
    def test_should_check_all_contractors_status(self, check_company_status_mock):
        check_company_status_for_all_contractors()

        assert check_company_status_mock.call_count == 1

    @patch("companies.govs_adapters.ceidg_adapter.CEIDGAdapter.is_company_active")
    def test_should_check_company_status(self, is_company_active_mock):
        is_company_active_mock.return_value = self.active_status

        check_company_status(self.company.id)

        assert is_company_active_mock.call_args_list == [call("111111111")]
