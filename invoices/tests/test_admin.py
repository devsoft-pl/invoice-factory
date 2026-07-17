import pytest

from invoices.factories import (
    CorrectionInvoiceRelationFactory,
    InvoiceSellFactory,
    YearFactory,
)
from users.factories import UserFactory


@pytest.mark.django_db
class TestInvoiceAdmin:
    @pytest.fixture(autouse=True)
    def setup(self, client):
        self.admin_user = UserFactory(is_staff=True, is_superuser=True)
        client.force_login(self.admin_user)

    def test_changelist_does_not_n_plus_1_on_related_fields(
        self, client, django_assert_max_num_queries
    ):
        InvoiceSellFactory.create_batch(10)

        with django_assert_max_num_queries(15):
            response = client.get("/admin/invoices/invoice/")

        assert response.status_code == 200


@pytest.mark.django_db
class TestYearAdmin:
    @pytest.fixture(autouse=True)
    def setup(self, client):
        self.admin_user = UserFactory(is_staff=True, is_superuser=True)
        client.force_login(self.admin_user)

    def test_changelist_does_not_n_plus_1_on_related_fields(
        self, client, django_assert_max_num_queries
    ):
        YearFactory.create_batch(10)

        with django_assert_max_num_queries(15):
            response = client.get("/admin/invoices/year/")

        assert response.status_code == 200


@pytest.mark.django_db
class TestCorrectionInvoiceRelationAdmin:
    @pytest.fixture(autouse=True)
    def setup(self, client):
        self.admin_user = UserFactory(is_staff=True, is_superuser=True)
        client.force_login(self.admin_user)

    def test_changelist_does_not_n_plus_1_on_related_fields(
        self, client, django_assert_max_num_queries
    ):
        CorrectionInvoiceRelationFactory.create_batch(10)

        with django_assert_max_num_queries(20):
            response = client.get("/admin/invoices/correctioninvoicerelation/")

        assert response.status_code == 200
