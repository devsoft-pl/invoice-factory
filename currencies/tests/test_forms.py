import pytest

from currencies.factories import CurrencyDictFactory, CurrencyFactory
from currencies.forms import CurrencyForm
from users.factories import UserFactory


@pytest.mark.django_db
class TestCurrencyForm:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.user = UserFactory.create()

    def test_form_with_valid_data(self):
        data = CurrencyDictFactory(code="eur")
        form = CurrencyForm(current_user=self.user, data=data)

        assert form.is_valid()
        assert form.errors == {}

    def test_clean_currency_returns_error(self):
        currency = CurrencyFactory.create(user=self.user, code="pln")
        data = CurrencyDictFactory(code=currency.code)
        form = CurrencyForm(current_user=self.user, data=data)

        assert not form.is_valid()
        assert form.errors == {"code": ["Waluta już istnieje"]}
