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
    def test_list_companies_if_not_logged(self):
        url = reverse("companies:list_companies")
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, f"/users/login/?next={url}")

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


class TestDetailCompany(TestCompany):
    def test_detail_company_if_not_logged(self):
        url = reverse("companies:detail_company", args=[self.user_companies[0].pk])
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, f"/users/login/?next={url}")

    def test_detail_company_if_logged(self):
        company = self.user_companies[0]
        url = reverse("companies:detail_company", args=[company.pk])
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "companies/detail_company.html")
        self.assertEqual(company.pk, response.context["company"].pk)

    def test_return_404_if_not_my_company(self):
        company = self.other_company
        url = reverse("companies:detail_company", args=[company.pk])
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
