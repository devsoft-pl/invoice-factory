import pytest
from django.core.exceptions import ValidationError

from countries.factories import CountryFactory
from persons.factories import PersonFactory
from users.factories import UserFactory


@pytest.mark.django_db
class TestPersonModel:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.person = PersonFactory.create()

    def test_returns_full_name(self):
        assert (
            self.person.full_name == f"{self.person.first_name} {self.person.last_name}"
        )

    def test_returns_str_full_name(self):
        assert (
            self.person.__str__() == f"{self.person.first_name} {self.person.last_name}"
        )


@pytest.mark.django_db
class TestPersonValidation:
    @pytest.fixture
    def user(self):
        return UserFactory()

    @pytest.fixture
    def polish_country(self, user):
        return CountryFactory(country="Polska", user=user)

    @pytest.fixture
    def foreign_country(self, user):
        return CountryFactory(country="Germany", user=user)

    def test_valid_polish_person_nip_and_zip_code(self, polish_country, user):
        person = PersonFactory.build(
            country=polish_country, nip="1234567890", zip_code="12-345", user=user
        )
        person.full_clean()  # Should not raise ValidationError

    @pytest.mark.parametrize(
        "invalid_nip", ["123", "12345678901", "abcdefghij", "123-456-789"]
    )
    def test_invalid_polish_nip(self, polish_country, invalid_nip, user):
        person = PersonFactory.build(country=polish_country, nip=invalid_nip, user=user)
        with pytest.raises(ValidationError) as e:
            person.full_clean()
        assert "nip" in e.value.error_dict

    def test_invalid_polish_zip_code(self, polish_country, user):
        person = PersonFactory.build(
            country=polish_country, zip_code="12345", user=user
        )
        with pytest.raises(ValidationError) as e:
            person.full_clean()
        assert "zip_code" in e.value.error_dict

    def test_valid_foreign_person_vat_and_zip_code(self, foreign_country, user):
        person = PersonFactory.build(
            country=foreign_country, nip="DE123456789", zip_code="D-12345", user=user
        )
        person.full_clean()  # Should not raise ValidationError

    def test_invalid_foreign_vat_number(self, foreign_country, user):
        person = PersonFactory.build(country=foreign_country, nip="DE123!@#", user=user)
        with pytest.raises(ValidationError) as e:
            person.full_clean()
        assert "nip" in e.value.error_dict

    def test_invalid_foreign_zip_code(self, foreign_country, user):
        person = PersonFactory.build(
            country=foreign_country, zip_code="123$%^", user=user
        )
        with pytest.raises(ValidationError) as e:
            person.full_clean()
        assert "zip_code" in e.value.error_dict

    def test_validation_error_if_country_is_none(self, user):
        person = PersonFactory.build(
            country=None, nip="anything", zip_code="anything", user=user
        )
        with pytest.raises(ValidationError) as e:
            person.full_clean()
        assert "country" in e.value.error_dict
