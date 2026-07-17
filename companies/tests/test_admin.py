import pytest

from companies.factories import CompanyFactory
from users.factories import UserFactory


@pytest.mark.django_db
class TestCompanyAdmin:
    @pytest.fixture(autouse=True)
    def setup(self, client):
        self.admin_user = UserFactory(is_staff=True, is_superuser=True)
        client.force_login(self.admin_user)

    def test_changelist_does_not_n_plus_1_on_related_fields(
        self, client, django_assert_max_num_queries
    ):
        CompanyFactory.create_batch(10)

        with django_assert_max_num_queries(15):
            response = client.get("/admin/companies/company/")

        assert response.status_code == 200
