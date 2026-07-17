import pytest

from currencies.factories import CurrencyFactory, ExchangeRateFactory
from users.factories import UserFactory


@pytest.mark.django_db
class TestCurrencyAdmin:
    @pytest.fixture(autouse=True)
    def setup(self, client):
        self.admin_user = UserFactory(is_staff=True, is_superuser=True)
        client.force_login(self.admin_user)

    def test_changelist_does_not_n_plus_1_on_related_fields(
        self, client, django_assert_max_num_queries
    ):
        CurrencyFactory.create_batch(10)

        with django_assert_max_num_queries(15):
            response = client.get("/admin/currencies/currency/")

        assert response.status_code == 200


@pytest.mark.django_db
class TestExchangeRateAdmin:
    @pytest.fixture(autouse=True)
    def setup(self, client):
        self.admin_user = UserFactory(is_staff=True, is_superuser=True)
        client.force_login(self.admin_user)

    def test_changelist_does_not_n_plus_1_on_related_fields(
        self, client, django_assert_max_num_queries
    ):
        ExchangeRateFactory.create_batch(10)

        # list_display includes currency (FK); without list_select_related
        # each row re-queries it, so this must stay flat as rows grow.
        with django_assert_max_num_queries(15):
            response = client.get("/admin/currencies/exchangerate/")

        assert response.status_code == 200
