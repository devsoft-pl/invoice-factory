from unittest.mock import patch

import pytest

from invoices.receivers import send_goodbye_email, send_welcome_email
from users.factories import UserFactory


@pytest.mark.django_db
class TestSendEmail:
    @pytest.fixture(autouse=True)
    def set_up(self):
        self.user = UserFactory()
        self.user_without_mail = UserFactory(email="")

    @patch("invoices.receivers.send_mail")
    def test_send_welcome_mail_when_user_with_email_is_created(self, send_mail_mock):
        send_welcome_email(None, self.user, created=True)

        send_mail_mock.assert_called_once()

    @patch("invoices.receivers.send_mail")
    def test_not_send_welcome_mail_when_is_not_created(self, send_mail_mock):
        send_welcome_email(None, self.user, created=False)

        send_mail_mock.assert_not_called()

    @patch("invoices.receivers.send_mail")
    def test_not_send_welcome_mail_when_user_without_email_is_created(
        self, send_mail_mock
    ):
        send_welcome_email(None, self.user_without_mail, created=True)

        send_mail_mock.assert_not_called()

    @patch("invoices.receivers.send_mail")
    def test_send_goodbye_mail_when_user_with_email_is_delete(self, send_mail_mock):
        send_goodbye_email(None, self.user)

        send_mail_mock.asser_calles_onece()

    @patch("invoices.receivers.send_mail")
    def test_not_send_goodbye_mail_when_user_without_email_is_delete(
        self, send_mail_mock
    ):
        send_goodbye_email(None, self.user_without_mail)

        send_mail_mock.assert_not_called()
