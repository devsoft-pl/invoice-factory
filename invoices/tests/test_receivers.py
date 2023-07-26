import pytest

from users.factories import UserFactory


@pytest.mark.django_db
class TestSendEmail:

    @pytest.fixture(autouse=True)
    def set_up(self):
        self.user = UserFactory()
        self.email_sender = "sender@test.pl"
        self.subject = "Test tematu"
        self.content = "Test treści"

    def test_send_welcome_message_when_user_with_email_is_created(self):
        pass

