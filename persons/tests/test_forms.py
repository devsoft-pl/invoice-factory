import pytest

from countries.factories import CountryFactory
from persons.factories import PersonDictFactory
from persons.forms import PersonForm
from users.factories import UserFactory


@pytest.mark.django_db
class TestPersonForm:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.user = UserFactory.create()
        self.country = CountryFactory.create(user=self.user)

    def test_form_with_valid_data(self):
        data = PersonDictFactory(
            first_name="Jan",
            last_name="Kowalski",
            zip_code="01-450",
            city="Warszawa",
            country=self.country,
            email="test@test.pl",
            phone_number="123456789",
        )
        form = PersonForm(data=data, current_user=self.user)

        is_valid = form.is_valid()

        assert form.errors == {}
        assert is_valid

    def test_form_with_not_valid_data(self):
        data = PersonDictFactory(country=self.country)
        form = PersonForm(data=data, current_user=self.user)

        is_valid = form.is_valid()

        assert form.errors == {
            "first_name": ["Enter the first_name in letters only"],
            "last_name": ["Enter the last_name in letters only"],
            "zip_code": ["Wpisz kod pocztowy składający się z liczb w formacie xx-xxx"],
            "city": ["Wpisz miasto tylko w postaci liter"],
            "phone_number": [
                "Wprowadź numer telefonu składający się wyłącznie z 9 cyfr"
            ],
        }
        assert not is_valid
