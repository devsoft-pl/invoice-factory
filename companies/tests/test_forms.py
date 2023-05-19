import pytest

from companies.factories import CompanyFactory
from companies.forms import CompanyFilterForm
from companies.models import Company
from users.factories import UserFactory


@pytest.mark.django_db
class TestCompanyForm:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.user = UserFactory.create()
        self.company_1 = CompanyFactory.create(
            name="Devsoft", nip="1111111111", regon="1111111", user=self.user
        )
        self.company_2 = CompanyFactory.create(
            name="Microsoft", nip="2222222222", regon="2222222", user=self.user
        )

    def test_return_company_with_name_startswith(self):
        request_get = {"name": "Dev"}
        self.form = CompanyFilterForm(request_get)
        self.form.is_valid()
        companies_list = Company.my_clients.filter(user=self.user)
        companies_list = self.form.get_filtered_companies(companies_list)
        assert self.company_1.id == companies_list[0].id
        assert len(companies_list) == 1

    def test_return_company_with_exact_name(self):
        request_get = {"name": "Devsoft"}
        self.form = CompanyFilterForm(request_get)
        self.form.is_valid()
        companies_list = Company.my_clients.filter(user=self.user)
        companies_list = self.form.get_filtered_companies(companies_list)
        assert self.company_1.id == companies_list[0].id
        assert len(companies_list) == 1

    def test_returns_filtered_companies_with_similar_name(self):
        request_get = {"name": "soft"}
        self.form = CompanyFilterForm(request_get)
        self.form.is_valid()
        companies_list = Company.my_clients.filter(user=self.user)
        companies_list = self.form.get_filtered_companies(companies_list)
        assert len(companies_list) == 2

    def test_return_empty_list_when_company_name_not_exist(self):
        request_get = {"name": "Faktoria"}
        self.form = CompanyFilterForm(request_get)
        self.form.is_valid()
        companies_list = Company.my_clients.filter(user=self.user)
        companies_list = self.form.get_filtered_companies(companies_list)
        assert len(companies_list) == 0

    def test_return_company_with_nip(self):
        request_get = {"nip": "1111111111"}
        self.form = CompanyFilterForm(request_get)
        self.form.is_valid()
        companies_list = Company.my_clients.filter(user=self.user)
        companies_list = self.form.get_filtered_companies(companies_list)
        assert self.company_1.id == companies_list[0].id
        assert len(companies_list) == 1

    def test_return_empty_list_when_company_nip_not_exist(self):
        request_get = {"nip": "3333333333"}
        self.form = CompanyFilterForm(request_get)
        self.form.is_valid()
        companies_list = Company.my_clients.filter(user=self.user)
        companies_list = self.form.get_filtered_companies(companies_list)
        assert len(companies_list) == 0

    def test_return_company_with_regon(self):
        request_get = {"regon": "1111111"}
        self.form = CompanyFilterForm(request_get)
        self.form.is_valid()
        companies_list = Company.my_clients.filter(user=self.user)
        companies_list = self.form.get_filtered_companies(companies_list)
        assert self.company_1.id == companies_list[0].id
        assert len(companies_list) == 1

    def test_return_empty_list_when_company_regon_not_exist(self):
        request_get = {"nip": "3333333"}
        self.form = CompanyFilterForm(request_get)
        self.form.is_valid()
        companies_list = Company.my_clients.filter(user=self.user)
        companies_list = self.form.get_filtered_companies(companies_list)
        assert len(companies_list) == 0
