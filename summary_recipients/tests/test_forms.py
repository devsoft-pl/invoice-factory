import pytest

from companies.factories import CompanyFactory
from summary_recipients.factories import SummaryRecipientDictFactory
from summary_recipients.forms import SummaryRecipientForm


@pytest.mark.django_db
class TestSummaryRecipientForm:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.company = CompanyFactory.create()

    def test_form_with_valid_data(self):
        data = SummaryRecipientDictFactory(company=self.company, is_last_day=False)

        form = SummaryRecipientForm(data=data)

        assert form.is_valid()
        assert form.errors == {}

    def test_form_with_not_valid_data(self):
        data = SummaryRecipientDictFactory(
            email="test.pl", day="test", is_last_day=False
        )

        form = SummaryRecipientForm(data=data)

        assert not form.is_valid()
        assert form.errors == {
            "day": ["Enter a whole number."],
            "email": ["Enter a valid email address."],
        }

    def test_clean_day_returns_error(self):
        data = SummaryRecipientDictFactory(
            email="test@test.pl",
            day=5,
            is_last_day=True,
        )

        form = SummaryRecipientForm(data=data)

        assert not form.is_valid()
        assert form.errors == {"day": ["This field is not last day of month."]}
