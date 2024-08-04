import pytest

from accountants.factories import AccountantDictFactory
from accountants.forms import AccountantForm
from companies.factories import CompanyFactory


@pytest.mark.django_db
class TestAccountantForm:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.company = CompanyFactory.create()

    def test_form_with_valid_data(self):
        data = AccountantDictFactory(phone_number="123456789", company=self.company)

        form = AccountantForm(data=data)
        is_valid = form.is_valid()

        assert form.errors == {}
        assert is_valid

    def test_form_with_not_valid_data(self):
        data = AccountantDictFactory(company=self.company)

        form = AccountantForm(data=data)
        is_valid = form.is_valid()

        assert form.errors == {
            "phone_number": ["Please enter a phone using minimum 9 numbers"]
        }
        assert not is_valid
