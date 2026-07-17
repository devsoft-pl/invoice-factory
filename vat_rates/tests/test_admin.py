import pytest

from users.factories import UserFactory
from vat_rates.factories import VatRateFactory


@pytest.mark.django_db
class TestVatRateAdmin:
    @pytest.fixture(autouse=True)
    def setup(self, client):
        self.admin_user = UserFactory(is_staff=True, is_superuser=True)
        client.force_login(self.admin_user)

    def test_changelist_does_not_n_plus_1_on_related_fields(
        self, client, django_assert_max_num_queries
    ):
        VatRateFactory.create_batch(10)

        with django_assert_max_num_queries(15):
            response = client.get("/admin/vat_rates/vatrate/")

        assert response.status_code == 200
