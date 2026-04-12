import pytest

from companies.factories import CompanyDictFactory, CompanyFactory
from companies.forms import CompanyFilterForm, CompanyForm
from companies.models import Company
from countries.factories import CountryFactory
from countries.models import Country
from users.factories import UserFactory


@pytest.mark.django_db
class TestCompanyFilterForm:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.user = UserFactory.create()
        self.company_1 = CompanyFactory.create(
            name="Devsoft",
            nip="1111111111",
            regon="111111111",
            user=self.user,
            is_my_company=False,
        )
        self.company_2 = CompanyFactory.create(
            name="Microsoft",
            nip="2222222222",
            regon="222222222",
            user=self.user,
            is_my_company=False,
        )

    @pytest.mark.parametrize(
        "company_name, expected_count", [["Dev", 1], ["Devsoft", 1], ["soft", 2]]
    )
    def test_return_filtered_with_different_parts_of_company_name(
        self, company_name, expected_count
    ):
        request_get = {"name": company_name}

        self.form = CompanyFilterForm(request_get)
        self.form.is_valid()

        companies_list = Company.my_clients.filter(user=self.user)
        filtered_list = self.form.get_filtered_companies(companies_list)

        assert self.company_1.id == filtered_list[0].id
        assert filtered_list.count() == expected_count

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
        request_get = {"regon": "111111111"}

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


@pytest.mark.django_db
class TestCompanyFormValidation:
    @pytest.fixture
    def user(self):
        return UserFactory()

    @pytest.fixture
    def polish_country(self, user):
        return CountryFactory(country="Polska", user=user)

    @pytest.fixture
    def foreign_country(self, user):
        return CountryFactory(country="Germany", user=user)

    def test_valid_polish_company_form(self, user, polish_country):
        data = CompanyDictFactory(
            country=polish_country.pk,
            nip="1234567890",
            zip_code="12-345",
            regon="123456789",
            phone_number="123456789",
        )
        form = CompanyForm(data=data, current_user=user)
        assert form.is_valid(), form.errors

    def test_invalid_polish_nip_in_form(self, user, polish_country):
        data = CompanyDictFactory(country=polish_country.pk, nip="123")
        form = CompanyForm(data=data, current_user=user)
        assert not form.is_valid()
        assert "nip" in form.errors
        assert "Polish NIP must consist of 10 digits." in form.errors["nip"][0]

    def test_invalid_polish_zip_code_in_form(self, user, polish_country):
        data = CompanyDictFactory(country=polish_country.pk, zip_code="12345")
        form = CompanyForm(data=data, current_user=user)
        assert not form.is_valid()
        assert "zip_code" in form.errors
        assert (
            "Polish ZIP code must be in the format XX-XXX."
            in form.errors["zip_code"][0]
        )

    def test_valid_foreign_company_form(self, user, foreign_country):
        data = CompanyDictFactory(
            country=foreign_country.pk,
            nip="DE123456",
            zip_code="D-12345",
            regon="123456789",
            phone_number="123456789",
        )
        form = CompanyForm(data=data, current_user=user)
        assert form.is_valid(), form.errors

    def test_invalid_foreign_nip_in_form(self, user, foreign_country):
        data = CompanyDictFactory(country=foreign_country.pk, nip="DE123!@#")
        form = CompanyForm(data=data, current_user=user)
        assert not form.is_valid()
        assert "nip" in form.errors
        assert (
            "Foreign VAT number contains invalid characters or is incorrect length."
            in form.errors["nip"][0]
        )

    def test_clean_nip_returns_error(self, user, polish_country):
        existing_company = CompanyFactory(user=user, nip="1111111111")
        data = CompanyDictFactory(country=polish_country.pk, nip=existing_company.nip)
        form = CompanyForm(data=data, current_user=user)
        assert not form.is_valid()
        assert "nip" in form.errors
        assert "Nip already exists" in form.errors["nip"]

    def test_clean_regon_returns_error(self, user, polish_country):
        existing_company = CompanyFactory(user=user, regon="123456789")
        data = CompanyDictFactory(
            country=polish_country.pk, regon=existing_company.regon
        )
        form = CompanyForm(data=data, current_user=user)
        assert not form.is_valid()
        assert "regon" in form.errors
        assert "Regon already exists" in form.errors["regon"]

    def test_filtered_countries_current_user(self, user):
        CountryFactory(user=user)
        CountryFactory()  # Another user's country
        form = CompanyForm(current_user=user)
        form_countries_ids = form.fields["country"].queryset.values_list(
            "id", flat=True
        )
        user_countries_ids = Country.objects.filter(user=user).values_list(
            "id", flat=True
        )
        assert set(form_countries_ids) == set(user_countries_ids)
        assert form_countries_ids.count() == 1
