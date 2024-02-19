from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.urls import reverse
from parameterized import parameterized

from companies.factories import CompanyDictFactory, CompanyFactory
from companies.models import Company
from countries.factories import CountryFactory
from users.factories import UserFactory


class TestCompany(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.set_password("test")
        self.user.save()
        self.user_companies = CompanyFactory.create_batch(
            12, user=self.user, is_my_company=False
        )
        self.my_companies = CompanyFactory.create_batch(
            2, user=self.user, is_my_company=True
        )


class TestListCompanies(TestCompany):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("companies:list_companies")

    def test_list_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_list_if_logged(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        object_list = response.context["companies"]

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "companies/list_companies.html")
        self.assertTrue(len(object_list) == 10)
        self.assertListEqual(list(object_list), self.user_companies[:10])

    def test_list_my_companies_if_logged(self):
        self.client.login(username=self.user.email, password="test")

        url = reverse("companies:list_my_companies")

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "companies/list_my_companies.html")

    def test_returns_first_page_when_abc(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(f"{self.url}?page=abc")

        object_list = response.context["companies"]

        self.assertListEqual(list(object_list), self.user_companies[:10])

    @parameterized.expand([[2], [666]])
    def test_pagination_return_correct_list(self, page):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(f"{self.url}?page={page}")

        object_list = response.context["companies"]

        self.assertTrue(len(object_list) == 2)
        self.assertListEqual(list(object_list), self.user_companies[10:])


class TestDetailCompany(TestCompany):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.user_companies[0]
        self.url = reverse("companies:detail_company", args=[self.company.pk])

    def test_detail_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_detail_if_logged(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "companies/detail_company.html")
        self.assertEqual(self.company.pk, response.context["company"].pk)

    def test_return_404_if_not_my_company(self):
        self.client.login(username=self.user.email, password="test")

        other_company = CompanyFactory()
        url = reverse("companies:detail_company", args=[other_company.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)


class TestCreateCompany(TestCompany):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("companies:create_company")

    def test_create_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_create_invalid_form_display_errors(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "name", "To pole jest wymagane.")
        self.assertFormError(response.context["form"], "nip", "To pole jest wymagane.")

    def test_create_with_valid_data(self):
        self.client.login(username=self.user.email, password="test")

        country = CountryFactory.create(user=self.user)
        company_data = CompanyDictFactory(
            nip="123456789",
            regon="987654321",
            country=country.pk,
            zip_code="00-345",
            city="Warszawa",
            email="test@test.pl",
            phone_number="123456789",
            is_my_company=True,
        )

        url = reverse("companies:create_my_company")

        response = self.client.post(url, company_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("companies:list_my_companies"))
        self.assertTrue(
            Company.objects.filter(
                regon=company_data["regon"],
                nip=company_data["nip"],
                is_my_company=True,
                user=self.user,
            ).exists()
        )

    def test_create_client_with_valid_data(self):
        self.client.login(username=self.user.email, password="test")

        country = CountryFactory.create(user=self.user)
        client_data = CompanyDictFactory(
            nip="111111111",
            regon="222222222",
            country=country.pk,
            zip_code="00-345",
            city="Warszawa",
            email="test@test.pl",
            phone_number="123456789",
            is_my_company=False,
        )

        response = self.client.post(self.url, client_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("companies:list_companies"))
        self.assertTrue(
            Company.objects.filter(
                regon=client_data["regon"],
                nip=client_data["nip"],
                is_my_company=False,
                user=self.user,
            ).exists()
        )

    def test_get_form(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "companies/create_company.html")


class TestCreateCompanyAjax(TestCompany):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("companies:create_company_ajax")

    def test_create_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_create_invalid_form_display_errors(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.post(self.url, {})

        response_json = response.json()
        self.assertFalse(response_json["success"])
        self.assertEqual(response_json["errors"]["name"], ["To pole jest wymagane."])
        self.assertEqual(response_json["errors"]["nip"], ["To pole jest wymagane."])
        self.assertEqual(response_json["errors"]["regon"], ["To pole jest wymagane."])
        self.assertEqual(response_json["errors"]["country"], ["To pole jest wymagane."])
        self.assertEqual(response_json["errors"]["address"], ["To pole jest wymagane."])
        self.assertEqual(
            response_json["errors"]["zip_code"], ["To pole jest wymagane."]
        )
        self.assertEqual(response_json["errors"]["city"], ["To pole jest wymagane."])
        self.assertEqual(response.status_code, 200)

    def test_create_my_company_with_valid_data(self):
        self.client.login(username=self.user.email, password="test")

        country = CountryFactory.create(user=self.user)
        company_data = CompanyDictFactory(
            nip="123456789",
            regon="987654321",
            country=country.pk,
            zip_code="00-345",
            city="Warszawa",
            email="test@test.pl",
            phone_number="123456789",
            is_my_company=True,
        )

        url = reverse("companies:create_my_company_ajax")

        response = self.client.post(url, company_data)

        response_json = response.json()
        self.assertTrue(response_json["success"])
        self.assertEqual(response_json["name"], company_data["name"])
        self.assertTrue(
            Company.objects.filter(
                regon=company_data["regon"], is_my_company=True, user=self.user
            ).exists()
        )

    def test_create_client_with_valid_data(self):
        self.client.login(username=self.user.email, password="test")

        country = CountryFactory.create(user=self.user)
        company_data = CompanyDictFactory(
            nip="987654321",
            regon="123456789",
            country=country.pk,
            zip_code="00-345",
            city="Warszawa",
            email="test@test.pl",
            phone_number="123456789",
            is_my_company=False,
        )

        url = reverse("companies:create_company_ajax")

        response = self.client.post(url, company_data)

        response_json = response.json()
        self.assertTrue(response_json["success"])
        self.assertEqual(response_json["name"], company_data["name"])
        self.assertTrue(
            Company.objects.filter(
                regon=company_data["regon"], is_my_company=False, user=self.user
            ).exists()
        )

    def test_get_form(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "companies/create_company_ajax.html")


class TestReplaceCompany(TestCompany):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.user_companies[0]
        self.url = reverse("companies:replace_company", args=[self.company.pk])

    def test_replace_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_replace_invalid_form_display_errors(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "name", "To pole jest wymagane.")
        self.assertFormError(
            response.context["form"], "regon", "To pole jest wymagane."
        )

    def test_replace_with_valid_data(self):
        self.client.login(username=self.user.email, password="test")

        country = CountryFactory.create(user=self.user)
        company_data = CompanyDictFactory(
            nip="123456789",
            regon="987654321",
            country=country.pk,
            zip_code="00-345",
            city="Warszawa",
            email="test@test.pl",
            phone_number="123456789",
            is_my_company=True,
        )

        response = self.client.post(self.url, company_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("companies:list_companies"))
        self.assertTrue(
            Company.objects.filter(
                nip=company_data["nip"], is_my_company=False, user=self.user
            ).exists()
        )

    def test_replace_my_company_with_valid_data(self):
        self.client.login(username=self.user.email, password="test")

        company = self.my_companies[0]
        url = reverse("companies:replace_company", args=[company.pk])

        country = CountryFactory.create(user=self.user)
        company_data = CompanyDictFactory(
            nip="333333333",
            regon="444444444",
            country=country.pk,
            zip_code="00-345",
            city="Warszawa",
            email="test@test.pl",
            phone_number="555666777",
            is_my_company=True,
        )

        response = self.client.post(url, company_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("companies:list_my_companies"))
        self.assertTrue(
            Company.objects.filter(
                regon=company_data["regon"],
                nip=company_data["nip"],
                is_my_company=True,
                user=self.user,
            ).exists()
        )

    def test_return_404_if_not_company(self):
        self.client.login(username=self.user.email, password="test")

        other_company = CompanyFactory()
        url = reverse("companies:replace_company", args=[other_company.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_get_form(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "companies/replace_company.html")


class TestDeleteCompany(TestCompany):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.user_companies[0]
        self.my_company = self.my_companies[0]
        self.url = reverse("companies:delete_company", args=[self.company.pk])

    def test_delete_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_delete_if_logged(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        with self.assertRaises(ObjectDoesNotExist):
            Company.objects.get(pk=self.company.pk)
        self.assertEqual(response.status_code, 302)

    def test_delete_my_company_if_logged(self):
        self.client.login(username=self.user.email, password="test")

        url = reverse("companies:delete_company", args=[self.my_company.pk])

        response = self.client.get(url)

        with self.assertRaises(ObjectDoesNotExist):
            Company.objects.get(pk=self.my_company.pk)
        self.assertEqual(response.status_code, 302)

    def test_return_404_if_not_my_company(self):
        self.client.login(username=self.user.email, password="test")

        other_company = CompanyFactory()
        url = reverse("companies:delete_company", args=[other_company.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)


class TestSettingsCompany(TestCompany):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.user_companies[0]
        self.url = reverse("companies:settings_company", args=[self.company.pk])

    def test_settings_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_settings_if_logged(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "companies/settings_company.html")
        self.assertEqual(self.company.pk, response.context["company"].pk)

    def test_return_404_if_not_my_company(self):
        self.client.login(username=self.user.email, password="test")

        other_company = CompanyFactory()
        url = reverse("companies:settings_company", args=[other_company.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
