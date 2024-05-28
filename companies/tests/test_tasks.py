from unittest.mock import call, patch

import pytest
from celery.exceptions import Ignore

from companies.factories import CompanyFactory
from companies.tasks import (
    check_company_status,
    check_company_status_for_all_contractors,
)
from users.factories import UserFactory


@pytest.mark.django_db
class TestCompaniesStatusTasks:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.user = UserFactory.create()
        self.company = CompanyFactory.create(
            user=self.user, is_my_company=False, nip="111111111"
        )

    @patch("companies.tasks.check_company_status.apply_async")
    def test_should_check_all_contractors_status(self, check_company_status_mock):
        check_company_status_for_all_contractors()

        assert check_company_status_mock.call_count == 1

    @patch("companies.govs_adapters.ceidg_adapter.CEIDGAdapter.is_company_active")
    def test_should_check_company_status(self, is_company_active_mock):
        is_company_active_mock.return_value = True

        check_company_status(self.company.id)

        assert is_company_active_mock.call_args_list == [call("111111111")]

    @patch("companies.govs_adapters.ceidg_adapter.CEIDGAdapter.is_company_active")
    @patch("users.models.User.send_email")
    def test_send_mail_when_company_is_not_active(
        self, send_email_mock, is_company_active_mock
    ):
        is_company_active_mock.return_value = False
        check_company_status(self.company.id)

        send_email_mock.assert_called_once()

    @patch("companies.govs_adapters.ceidg_adapter.CEIDGAdapter.is_company_active")
    @patch("users.models.User.send_email")
    def test_not_send_mail_when_company_is_active(
        self, send_email_mock, is_company_active_mock
    ):
        is_company_active_mock.return_value = True
        check_company_status(self.company.id)

        send_email_mock.assert_not_called()

    def test_returns_raise_if_company_does_not_exist(self):
        with pytest.raises(Ignore):
            check_company_status(99999)
