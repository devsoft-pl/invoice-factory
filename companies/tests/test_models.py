import pytest
from django.core.exceptions import ValidationError

from companies.factories import CompanyFactory
from countries.factories import CountryFactory
from users.factories import UserFactory


@pytest.mark.django_db
class TestCompanyModel:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.company = CompanyFactory.create(is_my_company=True)

    def test_returns_str_company_name(self):
        assert self.company.__str__() == self.company.name


@pytest.mark.django_db
class TestCompanyValidation:
    @pytest.fixture
    def user(self):
        return UserFactory()

    @pytest.fixture
    def polish_country(self, user):
        return CountryFactory(country="Polska", user=user)

    @pytest.fixture
    def foreign_country(self, user):
        return CountryFactory(country="Germany", user=user)

    def test_valid_polish_nip_and_zip_code(self, polish_country, user):
        company = CompanyFactory.build(
            country=polish_country, nip="1234567890", zip_code="12-345", user=user
        )
        company.full_clean()

    @pytest.mark.parametrize(
        "invalid_nip", ["123", "12345678901", "abcdefghij", "123-456-789"]
    )
    def test_invalid_polish_nip(self, polish_country, invalid_nip, user):
        company = CompanyFactory.build(
            country=polish_country, nip=invalid_nip, user=user
        )
        with pytest.raises(ValidationError) as e:
            company.full_clean()
        assert "nip" in e.value.error_dict

    def test_invalid_polish_zip_code(self, polish_country, user):
        company = CompanyFactory.build(
            country=polish_country, zip_code="12345", user=user
        )
        with pytest.raises(ValidationError) as e:
            company.full_clean()
        assert "zip_code" in e.value.error_dict

    def test_valid_foreign_vat_and_zip_code(self, foreign_country, user):
        company = CompanyFactory.build(
            country=foreign_country, nip="DE123456789", zip_code="D-12345", user=user
        )
        company.full_clean()

    def test_invalid_foreign_vat_number(self, foreign_country, user):
        company = CompanyFactory.build(
            country=foreign_country, nip="DE123!@#", user=user
        )
        with pytest.raises(ValidationError) as e:
            company.full_clean()
        assert "nip" in e.value.error_dict

    def test_invalid_foreign_zip_code(self, foreign_country, user):
        company = CompanyFactory.build(
            country=foreign_country, zip_code="123$%^", user=user
        )
        with pytest.raises(ValidationError) as e:
            company.full_clean()
        assert "zip_code" in e.value.error_dict

    def test_validation_error_if_country_is_none(self, user):
        company = CompanyFactory.build(
            country=None, nip="anything", zip_code="anything", user=user
        )
        with pytest.raises(ValidationError) as e:
            company.full_clean()
        assert "country" in e.value.error_dict
