import pytest

from companies.factories import CompanyFactory, SummaryRecipientFactory


@pytest.mark.django_db
class TestCompanyModel:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.company = CompanyFactory.create(is_my_company=True)

    def test_returns_str_company_name(self):
        assert self.company.__str__() == self.company.name


@pytest.mark.django_db
class TestSummaryRecipientModel:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.summary_recipient = SummaryRecipientFactory.create()

    def test_returns_str_description(self):
        assert self.summary_recipient.__str__() == self.summary_recipient.description

