import pytest

from companies.models import Company


@pytest.mark.django_db
class CompanyModelTest:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.company_1 = Company.objects.create(
            name="Test Firma",
            nip="1111111111",
            regon="1111111",
            country="pln",
            address="Testowa 1",
            zip_code="11-111",
            city="Testowa",
            email="test@test.pl",
            phone_number="999999999",
        )

    def test_str_returns_company_name(self):
        assert self.company_1.__str__() == self.company_1.name
