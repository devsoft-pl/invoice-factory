from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.urls import reverse

from currencies.factories import CurrencyFactory
from currencies.models import Currency
from users.factories import UserFactory


class TestCurrency(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.set_password("test")
        self.user.save()
        self.user_currencies = CurrencyFactory.create_batch(12, user=self.user)
        self.other_currency = CurrencyFactory()


class TestListCurrencies(TestCurrency):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("currencies:list_currencies")

    def test_list_currencies_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_list_currencies(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(self.url)

        object_list = response.context["currencies"]

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "currencies/list_currencies.html")
        self.assertTrue(len(object_list) == 10)
        self.assertListEqual(list(object_list), self.user_currencies[:10])

    def test_list_currencies_second_pag(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(f"{self.url}?page=2")

        object_list = response.context["currencies"]

        self.assertTrue(len(object_list) == 2)
        self.assertListEqual(list(object_list), self.user_currencies[10:])

    def test_returns_last_page_when_non_existent(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(f"{self.url}?page=666")

        object_list = response.context["currencies"]

        self.assertListEqual(list(object_list), self.user_currencies[10:])

    def test_returns_first_page_when_abc(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(f"{self.url}?page=abc")

        object_list = response.context["currencies"]

        self.assertListEqual(list(object_list), self.user_currencies[:10])


class TestDeleteCurrency(TestCurrency):
    def setUp(self) -> None:
        super().setUp()
        self.currency = self.user_currencies[0]
        self.url = reverse("currencies:delete_currency", args=[self.currency.pk])

    def test_delete_currency_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_delete_currency(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(self.url)

        with self.assertRaises(ObjectDoesNotExist):
            Currency.objects.get(pk=self.currency.pk)
        self.assertEqual(response.status_code, 302)

    def test_return_404_if_not_my_currency(self):
        url = reverse("currencies:delete_currency", args=[self.other_currency.pk])
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)


class TestCreateCurrency(TestCurrency):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("currencies:create_currency")

    def test_create_currency_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_invalid_form_display_errors(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "code", "To pole jest wymagane.")
        self.assertTemplateUsed(response, "currencies/create_currency.html")

    def test_create_currency_with_valid_data(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.post(self.url, {"code": "PLN"})

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("currencies:list_currencies"))
        self.assertTrue(Currency.objects.filter(code="PLN", user=self.user).count(), 1)

    def test_create_currency_with_valid_data_and_next(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.post(
            self.url, {"code": "PLN", "next": reverse("invoices:create_invoice")}
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("invoices:create_invoice"))
        self.assertTrue(Currency.objects.filter(code="PLN", user=self.user).count(), 1)

    def test_get_form(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)


class TestReplaceCurrency(TestCurrency):
    def setUp(self) -> None:
        super().setUp()
        self.currency = self.user_currencies[0]
        self.url = reverse("currencies:replace_currency", args=[self.currency.pk])

    def test_replace_currency_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_return_404_if_not_my_currency(self):
        url = reverse("currencies:replace_currency", args=[self.other_currency.pk])
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_invalid_form_display_errors(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "code", "To pole jest wymagane.")
        self.assertTemplateUsed(response, "currencies/replace_currency.html")

    def test_replace_currency_with_valid_data(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.post(self.url, {"code": "USD"})

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("currencies:list_currencies"))
        self.assertTrue(Currency.objects.filter(code="USD", user=self.user).exists())

    def test_get_form(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
