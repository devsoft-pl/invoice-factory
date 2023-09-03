import pytest

from countries.factories import CountryFactory


@pytest.mark.django_db
class TestCountryModel:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.country = CountryFactory.create()

    def test_returns_str_country_name(self):
        assert self.country.__str__() == self.country.country
