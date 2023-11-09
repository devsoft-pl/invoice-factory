from unittest.mock import patch

import pytest

from summary_recipients.factories import SummaryRecipientFactory


@pytest.mark.django_db
class TestSummaryRecipientModel:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.summary_recipient = SummaryRecipientFactory.create()

    def test_returns_str_description(self):
        assert self.summary_recipient.__str__() == self.summary_recipient.description

    @patch("summary_recipients.models.EmailMessage.send")
    def test_returns_sent_email_without_attachment(self, email_message_send_mock):
        subject = "Test temat"
        content = "Test zawartość"
        self.summary_recipient.send_email(subject, content)

        email_message_send_mock.assert_called_once()

    @patch("summary_recipients.models.EmailMessage.attach")
    def test_returns_sent_email_with_attachment(self, email_message_attach_mock):
        subject = "Test temat"
        content = "Test zawartość"
        files = [{"name": "test.pdf", "content": "test"}]
        self.summary_recipient.send_email(subject, content, files)

        email_message_attach_mock.assert_called_once()
