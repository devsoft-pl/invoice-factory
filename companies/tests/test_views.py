from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.urls import reverse
from parameterized import parameterized

from companies.factories import (CompanyDictFactory, CompanyFactory,
                                 SummaryRecipientFactory)
from companies.models import Company, SummaryRecipient
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
        self.other_company = CompanyFactory()
        self.country = CountryFactory.create(user=self.user)


class TestListCompanies(TestCompany):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("companies:list_companies")
        self.my_url = reverse("companies:list_my_companies")

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

    def test_returns_first_page_when_abc(self):
        self.client.login(username=self.user.email, password="test")
        response = self.client.get(f"{self.url}?page=abc")

        object_list = response.context["companies"]

        self.assertListEqual(list(object_list), self.user_companies[:10])

    def test_list_my_companies_if_logged(self):
        self.client.login(username=self.user.email, password="test")
        response = self.client.get(self.my_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "companies/list_my_companies.html")

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
        url = reverse("companies:detail_company", args=[self.other_company.pk])
        self.client.login(username=self.user.email, password="test")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)


class TestDeleteCompany(TestCompany):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.user_companies[0]
        self.my_company = self.my_companies[0]
        self.url = reverse("companies:delete_company", args=[self.company.pk])
        self.my_url = reverse("companies:delete_company", args=[self.my_company.pk])

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
        response = self.client.get(self.my_url)

        with self.assertRaises(ObjectDoesNotExist):
            Company.objects.get(pk=self.my_company.pk)
        self.assertEqual(response.status_code, 302)

    def test_return_404_if_not_my_company(self):
        url = reverse("companies:delete_company", args=[self.other_company.pk])
        self.client.login(username=self.user.email, password="test")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)


class TestCreateCompany(TestCompany):
    def setUp(self) -> None:
        super().setUp()
        self.my_url = reverse("companies:create_my_company")
        self.url = reverse("companies:create_company")

    def test_create_if_not_logged(self):
        response = self.client.get(self.my_url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.my_url}")

    def test_invalid_form_display_errors(self):
        self.client.login(username=self.user.email, password="test")
        response = self.client.post(self.my_url, {})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "name", "To pole jest wymagane.")
        self.assertFormError(response.context["form"], "nip", "To pole jest wymagane.")
        self.assertTemplateUsed(response, "companies/create_company.html")

    def test_create_with_valid_data(self):
        company_data = CompanyDictFactory(
            nip="123456789",
            regon="987654321",
            country=self.country.pk,
            zip_code="00-345",
            city="Warszawa",
            email="test@test.pl",
            phone_number="123456789",
            is_my_company=True
        )
        self.client.login(username=self.user.email, password="test")

        response = self.client.post(self.my_url, company_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("companies:list_my_companies"))
        self.assertTrue(
            Company.objects.filter(
                regon="987654321", nip="123456789", is_my_company=True, user=self.user
            ).exists()
        )

    def test_create_contractor_with_valid_data(self):
        client_data = CompanyDictFactory(
            nip="111111111",
            regon="222222222",
            country=self.country.pk,
            zip_code="00-345",
            city="Warszawa",
            email="test@test.pl",
            phone_number="123456789",
            is_my_company=False
        )
        self.client.login(username=self.user.email, password="test")
        response = self.client.post(self.url, client_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("companies:list_companies"))
        self.assertTrue(
            Company.objects.filter(
                regon="222222222", nip="111111111", is_my_company=False, user=self.user
            ).exists()
        )

    def test_get_form(self):
        self.client.login(username=self.user.email, password="test")
        response = self.client.get(self.my_url)

        self.assertEqual(response.status_code, 200)


class TestReplaceCompany(TestCompany):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.user_companies[0]
        self.url = reverse("companies:replace_company", args=[self.company.pk])

    def test_replace_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_return_404_if_not_company(self):
        url = reverse("companies:replace_company", args=[self.other_company.pk])
        self.client.login(username=self.user.email, password="test")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_invalid_form_display_errors(self):
        self.client.login(username=self.user.email, password="test")
        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "name", "To pole jest wymagane.")
        self.assertFormError(
            response.context["form"], "regon", "To pole jest wymagane."
        )
        self.assertTemplateUsed(response, "companies/replace_company.html")

    def test_replace_with_valid_data(self):
        company_data = CompanyDictFactory(
            nip="123456789",
            regon="987654321",
            country=self.country.pk,
            zip_code="00-345",
            city="Warszawa",
            email="test@test.pl",
            phone_number="123456789",
            is_my_company=True
        )
        self.client.login(username=self.user.email, password="test")

        response = self.client.post(self.url, company_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("companies:list_companies"))
        self.assertTrue(
            Company.objects.filter(
                nip="123456789", is_my_company=False, user=self.user
            ).exists()
        )

    def test_replace_my_company_with_valid_data(self):
        company = self.my_companies[0]
        url = reverse("companies:replace_company", args=[company.pk])
        self.company_data = {
            "name": "test",
            "nip": "123456789",
            "regon": "987654321",
            "country": self.country.pk,
            "address": "ulica testowa",
            "zip_code": "00-345",
            "city": "Warszawa",
            "email": "test@test.pl",
            "is_my_company": True,
        }
        self.client.login(username=self.user.email, password="test")

        response = self.client.post(url, self.company_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("companies:list_my_companies"))
        self.assertTrue(
            Company.objects.filter(
                name="test", nip="123456789", is_my_company=True, user=self.user
            ).exists()
        )

    def test_get_form(self):
        self.client.login(username=self.user.email, password="test")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)


class TestSummaryRecipient(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.set_password("test")
        self.user.save()
        self.user_company = CompanyFactory.create(user=self.user, is_my_company=True)
        self.other_company = CompanyFactory()
        self.summary_recipient = SummaryRecipientFactory.create(
            company=self.user_company
        )
        self.other_summary_recipient = SummaryRecipientFactory.create()


class TestListSummaryRecipients(TestSummaryRecipient):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse(
            "companies:list_summary_recipients", args=[self.user_company.pk]
        )

    def test_list_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_list_if_logged(self):
        self.client.login(username=self.user.email, password="test")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "companies/list_summary_recipients.html")

    def test_return_404_if_not_company(self):
        url = reverse("companies:list_summary_recipients", args=[self.other_company.pk])
        self.client.login(username=self.user.email, password="test")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)


class TestDeleteSummaryRecipient(TestSummaryRecipient):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse(
            "companies:delete_summary_recipient", args=[self.summary_recipient.pk]
        )
        self.other_url = reverse(
            "companies:delete_summary_recipient", args=[self.other_summary_recipient.pk]
        )

    def test_delete_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_delete_if_logged(self):
        self.client.login(username=self.user.email, password="test")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)

    def test_not_delete_if_other_owner_company(self):
        self.client.login(username=self.user.email, password="test")
        response = self.client.get(self.other_url)

        self.assertEqual(response.status_code, 404)


class TestCreateSummaryRecipient(TestSummaryRecipient):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse(
            "companies:create_summary_recipient", args=[self.user_company.pk]
        )

    def test_create_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_get_form(self):
        self.client.login(username=self.user.email, password="test")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_invalid_form_display_errors(self):
        self.client.login(username=self.user.email, password="test")
        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "description", "To pole jest wymagane."
        )
        self.assertFormError(response.context["form"], "day", "To pole jest wymagane.")
        self.assertFormError(
            response.context["form"], "email", "To pole jest wymagane."
        )
        self.assertFormError(
            response.context["form"], "settlement_types", "To pole jest wymagane."
        )
        self.assertTemplateUsed(response, "companies/create_summary_recipient.html")

    def test_create_with_valid_data(self):
        summary_recipient_data = {
            "description": "test",
            "company": self.user_company.pk,
            "day": 1,
            "email": "test@test.pl",
            "settlement_types": SummaryRecipient.MONTHLY,
        }
        self.client.login(username=self.user.email, password="test")
        response = self.client.post(self.url, summary_recipient_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse("companies:list_summary_recipients", args=[self.user_company.pk]),
        )
        self.assertTrue(
            SummaryRecipient.objects.filter(
                description="test", day=1, email="test@test.pl"
            ).exists()
        )

    def test_return_404_if_not_my_company(self):
        url = reverse(
            "companies:create_summary_recipient", args=[self.other_company.pk]
        )
        self.client.login(username=self.user.email, password="test")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)


class TestReplaceSummaryRecipient(TestSummaryRecipient):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse(
            "companies:replace_summary_recipient", args=[self.summary_recipient.pk]
        )
        self.other_url = reverse(
            "companies:replace_summary_recipient",
            args=[self.other_summary_recipient.pk],
        )

    def test_replace_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_not_replace_if_other_owner_company(self):
        self.client.login(username=self.user.email, password="test")
        response = self.client.get(self.other_url)

        self.assertEqual(response.status_code, 404)

    def test_get_form(self):
        self.client.login(username=self.user.email, password="test")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_replace_with_valid_data(self):
        summary_recipient_data = {
            "description": "test",
            "company": self.user_company.pk,
            "day": 1,
            "email": "test@test.pl",
            "settlement_types": SummaryRecipient.MONTHLY,
        }
        self.client.login(username=self.user.email, password="test")

        response = self.client.post(self.url, summary_recipient_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse("companies:list_summary_recipients", args=[self.user_company.pk]),
        )
        self.assertTrue(
            SummaryRecipient.objects.filter(
                description="test", day=1, email="test@test.pl"
            ).exists()
        )
