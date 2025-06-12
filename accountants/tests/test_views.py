from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from accountants.factories import AccountantDictFactory, AccountantFactory
from accountants.models import Accountant
from companies.factories import CompanyFactory
from users.factories import UserFactory


class TestAccountant(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.set_password("test")
        self.user.save()
        self.company = CompanyFactory.create(user=self.user, is_my_company=True)


class TestListAccountant(TestAccountant):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("accountants:list_accountants", args=[self.company.pk])

    def test_list_if_not_logged(self):
        response = self.client.get(self.url, fOllow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_list_if_logged(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accountants/list_accountants.html")

    def test_return_404_if_not_company(self):
        self.client.login(username=self.user.email, password="test")

        other_company = CompanyFactory()
        url = reverse("accountants:list_accountants", args=[other_company.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)


class TestCreateAccountant(TestAccountant):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("accountants:create_accountant", args=[self.company.pk])

    def test_create_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_create_invalid_form_display_errors(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "email", _("This field is required.")
        )
        self.assertFormError(
            response.context["form"], "name", _("This field is required.")
        )

    def test_create_with_valid_data(self):
        self.client.login(username=self.user.email, password="test")

        accountant_data = AccountantDictFactory(
            email="test@test.pl", phone_number="123456789"
        )

        response = self.client.post(self.url, accountant_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse("accountants:list_accountants", args=[self.company.pk])
        )
        self.assertTrue(
            Accountant.objects.filter(
                email=accountant_data["email"],
                phone_number=accountant_data["phone_number"],
            ).exists()
        )

    def test_return_404_if_not_company(self):
        self.client.login(username=self.user.email, password="test")

        other_company = CompanyFactory()
        url = reverse("accountants:create_accountant", args=[other_company.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_get_form(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accountants/create_accountant.html")


class TestReplaceAccountant(TestAccountant):
    def setUp(self) -> None:
        super().setUp()
        self.accountant = AccountantFactory.create(company=self.company)
        self.url = reverse("accountants:replace_accountant", args=[self.accountant.pk])

    def test_replace_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_replace_invalid_form_display_errors(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "email", _("This field is required.")
        )
        self.assertFormError(
            response.context["form"], "name", _("This field is required.")
        )

    def test_replace_with_valid_data(self):
        self.client.login(username=self.user.email, password="test")

        accountant_data = AccountantDictFactory(
            email="test2@test.pl", phone_number="987654321"
        )

        response = self.client.post(self.url, accountant_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse("accountants:list_accountants", args=[self.company.pk])
        )
        self.assertTrue(
            Accountant.objects.filter(
                name=accountant_data["name"],
                email=accountant_data["email"],
            ).exists()
        )

    def test_return_404_if_not_accountant(self):
        self.client.login(username=self.user.email, password="test")

        other_accountant = AccountantFactory()
        url = reverse("accountants:replace_accountant", args=[other_accountant.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_get_form(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accountants/replace_accountant.html")


class TestDeleteAccountant(TestAccountant):
    def setUp(self) -> None:
        super().setUp()
        self.accountant = AccountantFactory.create(company=self.company)
        self.url = reverse("accountants:delete_accountant", args=[self.accountant.pk])

    def test_delete_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_delete_if_logged(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        with self.assertRaises(ObjectDoesNotExist):
            Accountant.objects.get(pk=self.accountant.pk)
        self.assertEqual(response.status_code, 302)

    def test_return_404_if_not_my_accountant(self):
        self.client.login(username=self.user.email, password="test")

        other_accountant = AccountantFactory()
        url = reverse("accountants:delete_accountant", args=[other_accountant.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
