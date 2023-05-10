import pytest

from countries.models import Country


@pytest.mark.django_db
class TestCountryModels:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.country = Country.objects.create(country="pln")

    def test_str_returns_country_name(self):
        assert self.country.__str__() == self.country.country
