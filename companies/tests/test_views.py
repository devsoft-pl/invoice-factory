from django.test import TestCase
from django.urls import reverse

from companies.factories import CompanyFactory
from users.factories import UserFactory


class TestCompany(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.set_password("test")
        self.user.save()
        self.user_companies = CompanyFactory.create_batch(12, user=self.user)
        self.other_company = CompanyFactory()


class TestListCompanies(TestCompany):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("companies:list_companies")

    def test_list_companies_if_not_logged(self):
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_list_companies_if_logged(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(self.url)

        object_list = response.context["companies"]

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "companies/list_companies.html")
        self.assertTrue(len(object_list) == 10)
        self.assertListEqual(list(object_list), self.user_companies[:10])

    def test_list_companies_second_pag(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(f"{self.url}?page=2")

        object_list = response.context["companies"]

        self.assertTrue(len(object_list) == 2)
        self.assertListEqual(list(object_list), self.user_companies[10:])


class TestDetailCompany(TestCompany):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.user_companies[0]
        self.url = reverse("companies:detail_company", args=[self.company.pk])

    def test_detail_company_if_not_logged(self):
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_detail_company_if_logged(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "companies/detail_company.html")
        self.assertEqual(self.company.pk, response.context["company"].pk)

    def test_return_404_if_not_my_company(self):
        url = reverse("companies:detail_company", args=[self.other_company.pk])
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
