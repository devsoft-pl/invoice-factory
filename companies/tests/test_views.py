import pytest
from django.test import RequestFactory

from companies.factories import ClientCompanyFactory
from companies.views import list_companies_view
from users.factories import UserFactory


@pytest.mark.django_db
class TestCompanyView:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.rf = RequestFactory()
        self.user = UserFactory()
        self.company = ClientCompanyFactory.create(user=self.user)

    def test_list_companies_view_returns_200(self):
        request = self.rf.get("/companies/")
        request.user = self.user
        response = list_companies_view(request)
        assert response.status_code == 200

    def test_list_companies_returns_company(self):
        request = self.rf.get("/companies/")
        request.user = self.user
        response = list_companies_view(request)
        assert self.company.name in str(response.content)
