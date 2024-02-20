import pytest

from countries.factories import CountryDictFactory, CountryFactory
from countries.forms import CountryForm
from users.factories import UserFactory


@pytest.mark.django_db
class TestCountryForm:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.user = UserFactory.create()

    def test_form_with_valid_data(self):
        data = CountryDictFactory()
        form = CountryForm(current_user=self.user, data=data)
        is_valid = form.is_valid()

        assert form.errors == {}
        assert is_valid

    def test_clean_country_returns_error(self):
        country = CountryFactory.create(user=self.user)
        data = CountryDictFactory(country=country.country)
        form = CountryForm(current_user=self.user, data=data)
        is_valid = form.is_valid()

        assert form.errors == {"country": ["Kraj już istnieje"]}
        assert not is_valid
