from django.test import TestCase
from django.urls import reverse

from companies.factories import CompanyFactory
from countries.factories import CountryFactory
from users.factories import UserFactory


class TestComapny(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.set_password("test")
        self.user.save()
        self.user_companies = CompanyFactory.create_batch(12, user=self.user)
        self.user_company = CompanyFactory()

    def test_list_companies_if_not_logged(self):
        url = reverse("companies:list_companies")
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, "/users/login/?next=/companies/")

    def test_list_companies_if_logged(self):
        url = reverse("companies:list_companies")
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(url)

        object_list = response.context["companies"]

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "companies/list_companies.html")
        self.assertTrue(len(object_list) == 10)
        self.assertListEqual(list(object_list), self.user_companies[:10])

    def test_list_companies_second_pag(self):
        url = reverse("companies:list_companies")
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(f"{url}?page=2")

        object_list = response.context["companies"]

        self.assertTrue(len(object_list) == 2)
        self.assertListEqual(list(object_list), self.user_companies[10:])
