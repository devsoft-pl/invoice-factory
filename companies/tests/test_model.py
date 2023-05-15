import pytest

from companies.factories import MyCompanyFactory


@pytest.mark.django_db
class TestCompanyModel:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.my_company = MyCompanyFactory.create()

    def test_str_returns_company_name(self):
        assert self.my_company.__str__() == self.my_company.name
