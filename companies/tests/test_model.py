import pytest

from companies.models import Company
from countries.models import Country


@pytest.mark.django_db
class TestCompanyModel:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        country = Country.objects.create(country="pln")
        self.company = Company.objects.create(
            name="Test Firma",
            nip="1111111111",
            regon="1111111",
            country=country,
            address="Testowa 1",
            zip_code="11-111",
            city="Testowa",
            email="test@test.pl",
            phone_number="999999999",
        )

    def test_str_returns_company_name(self):
        assert self.company.__str__() == self.company.name
