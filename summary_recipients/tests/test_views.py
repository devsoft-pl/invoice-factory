from django.test import TestCase
from django.urls import reverse

from companies.factories import CompanyFactory
from summary_recipients.factories import SummaryRecipientFactory
from summary_recipients.models import SummaryRecipient
from users.factories import UserFactory


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
