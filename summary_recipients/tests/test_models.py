import pytest

from summary_recipients.factories import SummaryRecipientFactory


@pytest.mark.django_db
class TestSummaryRecipientModel:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.summary_recipient = SummaryRecipientFactory.create()

    def test_returns_str_description(self):
        assert self.summary_recipient.__str__() == self.summary_recipient.description
