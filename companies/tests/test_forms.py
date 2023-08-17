import pytest

from companies.factories import CompanyDictFactory, CompanyFactory
from companies.forms import CompanyFilterForm, CompanyForm
from companies.models import Company
from countries.factories import CountryFactory
from countries.models import Country
from users.factories import UserFactory


@pytest.mark.django_db
class TestCompanyForm:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.user = UserFactory.create()
        self.country_1 = CountryFactory.create(user=self.user)
        self.country_2 = CountryFactory.create()
        self.company_1 = CompanyFactory.create(
            name="Devsoft", nip="1111111111", regon="1111111", user=self.user
        )
        self.company_2 = CompanyFactory.create(
            name="Microsoft", nip="2222222222", regon="2222222", user=self.user
        )

    def test_return_filtered_company_with_name_startswith(self):
        request_get = {"name": "Dev"}
        self.form = CompanyFilterForm(request_get)
        self.form.is_valid()
        companies_list = Company.my_clients.filter(user=self.user)
        filtered_list = self.form.get_filtered_companies(companies_list)
        assert self.company_1.id == filtered_list[0].id
        assert filtered_list.count() == 1

    def test_return_filtered_company_with_exact_name(self):
        request_get = {"name": "Devsoft"}
        self.form = CompanyFilterForm(request_get)
        self.form.is_valid()
        companies_list = Company.my_clients.filter(user=self.user)
        filtered_list = self.form.get_filtered_companies(companies_list)
        assert self.company_1.id == filtered_list[0].id
        assert filtered_list.count() == 1

    def test_returns_filtered_companies_with_similar_name(self):
        request_get = {"name": "soft"}
        self.form = CompanyFilterForm(request_get)
        self.form.is_valid()
        companies_list = Company.my_clients.filter(user=self.user)
        filtered_list = self.form.get_filtered_companies(companies_list)
        assert filtered_list.count() == 2

    def test_return_filtered_empty_list_when_company_name_not_exist(self):
        request_get = {"name": "Faktoria"}
        self.form = CompanyFilterForm(request_get)
        self.form.is_valid()
        companies_list = Company.my_clients.filter(user=self.user)
        filtered_list = self.form.get_filtered_companies(companies_list)
        assert filtered_list.count() == 0

    def test_return_filtered_company_with_nip(self):
        request_get = {"nip": "1111111111"}
        self.form = CompanyFilterForm(request_get)
        self.form.is_valid()
        companies_list = Company.my_clients.filter(user=self.user)
        filtered_list = self.form.get_filtered_companies(companies_list)
        assert self.company_1.id == filtered_list[0].id
        assert filtered_list.count() == 1

    def test_return_filtered_empty_list_when_company_nip_not_exist(self):
        request_get = {"nip": "3333333333"}
        self.form = CompanyFilterForm(request_get)
        self.form.is_valid()
        companies_list = Company.my_clients.filter(user=self.user)
        filtered_list = self.form.get_filtered_companies(companies_list)
        assert filtered_list.count() == 0

    def test_return_filtered_company_with_regon(self):
        request_get = {"regon": "1111111"}
        self.form = CompanyFilterForm(request_get)
        self.form.is_valid()
        companies_list = Company.my_clients.filter(user=self.user)
        filtered_list = self.form.get_filtered_companies(companies_list)
        assert self.company_1.id == filtered_list[0].id
        assert filtered_list.count() == 1

    def test_return_filtered_empty_list_when_company_regon_not_exist(self):
        request_get = {"nip": "3333333"}
        self.form = CompanyFilterForm(request_get)
        self.form.is_valid()
        companies_list = Company.my_clients.filter(user=self.user)
        filtered_list = self.form.get_filtered_companies(companies_list)
        assert filtered_list.count() == 0

    def test_filtered_countries_current_user(self):
        self.form = CompanyForm(current_user=self.user)
        form_countries_ids = self.form.fields["country"].queryset.values_list(
            "id", flat=True
        )
        user_countries_ids = Country.objects.filter(user=self.user).values_list(
            "id", flat=True
        )
        assert set(form_countries_ids) == set(user_countries_ids)
        assert form_countries_ids.count() == user_countries_ids.count()

    def test_form_with_valid_data(self):
        data = CompanyDictFactory(country=self.country_1)
        form = CompanyForm(data=data, current_user=self.user)
        assert form.is_valid()
        assert form.errors == {}

    def test_clean_nip_returns_error(self):
        data = CompanyDictFactory(country=self.country_1, nip=self.company_1.nip)
        form = CompanyForm(data=data, current_user=self.user)
        assert not form.is_valid()
        assert form.errors == {"nip": ["Nip już istnieje"]}

    def test_clean_regon_returns_error(self):
        data = CompanyDictFactory(country=self.country_1, regon=self.company_1.regon)
        form = CompanyForm(data=data, current_user=self.user)
        assert not form.is_valid()
        assert form.errors == {"regon": ["Regon już istnieje"]}
