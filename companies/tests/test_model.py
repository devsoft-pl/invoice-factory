import pytest

from companies.factories import CompanyFactory


@pytest.mark.django_db
class TestCompanyModel:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.my_company = CompanyFactory.create(is_my_company=True)

    def test_str_returns_company_name(self):
        assert self.my_company.__str__() == self.my_company.name
