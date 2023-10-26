import pytest

from accountants.factories import AccountantDictFactory, AccountantFactory
from accountants.forms import AccountantForm
from users.factories import UserFactory


@pytest.mark.django_db
class TestAccountantForm:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.user = UserFactory.create()
        self.accountant = AccountantFactory.create(user=self.user)

    def test_form_with_valid_data(self):
        data = AccountantDictFactory(phone_number="123456789", email="test@test.pl")
        form = AccountantForm(data=data, user=self.user)

        assert form.is_valid()
        assert form.errors == {}

    def test_form_with_not_valid_data(self):
        data = AccountantDictFactory(email="test@test.pl")
        form = AccountantForm(data=data, user=self.user)

        assert not form.is_valid()
        assert form.errors == {
            "phone_number": [
                "Wprowadź numer telefonu składający się wyłącznie z 9 cyfr"
            ],
        }
