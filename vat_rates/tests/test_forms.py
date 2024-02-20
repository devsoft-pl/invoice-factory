import pytest

from users.factories import UserFactory
from vat_rates.factories import VatRateDictFactory, VatRateFactory
from vat_rates.forms import VatRateForm


@pytest.mark.django_db
class TestVatRateForm:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.user = UserFactory.create()

    def test_form_with_valid_data(self):
        data = VatRateDictFactory()
        form = VatRateForm(current_user=self.user, data=data)

        assert form.is_valid()
        assert form.errors == {}

    def test_clean_rate_returns_error(self):
        rate = VatRateFactory.create(user=self.user, rate="23")
        data = VatRateDictFactory(rate=rate.rate)
        form = VatRateForm(current_user=self.user, data=data)

        assert not form.is_valid()
        assert form.errors == {"rate": ["Stawka VAT już istnieje"]}
