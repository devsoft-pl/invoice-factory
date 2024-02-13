from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.urls import reverse
from parameterized import parameterized

from currencies.factories import CurrencyDictFactory, CurrencyFactory
from currencies.models import Currency
from users.factories import UserFactory


class TestCurrency(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.set_password("test")
        self.user.save()
        self.user_currencies = CurrencyFactory.create_batch(12, user=self.user)


class TestListCurrencies(TestCurrency):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("currencies:list_currencies")

    def test_list_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_list_if_logged(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        object_list = response.context["currencies"]

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "currencies/list_currencies.html")
        self.assertTrue(len(object_list) == 10)
        self.assertListEqual(list(object_list), self.user_currencies[:10])

    def test_returns_first_page_when_abc(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(f"{self.url}?page=abc")

        object_list = response.context["currencies"]

        self.assertListEqual(list(object_list), self.user_currencies[:10])

    @parameterized.expand([[2], [666]])
    def test_pagination_return_correct_list(self, page):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(f"{self.url}?page={page}")

        object_list = response.context["currencies"]

        self.assertTrue(len(object_list) == 2)
        self.assertListEqual(list(object_list), self.user_currencies[10:])


class TestCreateCurrency(TestCurrency):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("currencies:create_currency")

    def test_create_currency_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_invalid_form_display_errors(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "code", "To pole jest wymagane.")
        self.assertTemplateUsed(response, "currencies/create_currency.html")

    def test_create_with_valid_data(self):
        self.client.login(username=self.user.email, password="test")

        currency_data = CurrencyDictFactory(code="PLN")
        response = self.client.post(self.url, currency_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("currencies:list_currencies"))
        self.assertTrue(
            Currency.objects.filter(code=currency_data["code"], user=self.user).count(),
            1,
        )

    def test_create_with_valid_data_and_next(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.post(
            self.url, {"code": "PLN", "next": reverse("invoices:create_sell_invoice")}
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("invoices:create_sell_invoice"))
        self.assertTrue(Currency.objects.filter(code="PLN", user=self.user).count(), 1)

    def test_get_form(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)


class TestCreateCurrencyAjax(TestCurrency):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("currencies:create_currency_ajax")

    def test_create_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_create_invalid_form_display_errors(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.post(self.url, {})

        response_json = response.json()
        self.assertFalse(response_json["success"])
        self.assertEqual(response_json["errors"]["code"], ["To pole jest wymagane."])
        self.assertEqual(response.status_code, 200)

    def test_create_with_valid_data(self):
        self.client.login(username=self.user.email, password="test")

        currency_data = CurrencyDictFactory(code="pln")

        response = self.client.post(self.url, currency_data)

        response_json = response.json()
        self.assertTrue(response_json["success"])
        self.assertEqual(response_json["name"], "PLN")
        self.assertTrue(
            Currency.objects.filter(
                code=currency_data["code"], user=self.user
            ).count(),
            1,
        )
        self.assertEqual(response.status_code, 200)

    def test_get_form(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)


class TestReplaceCurrency(TestCurrency):
    def setUp(self) -> None:
        super().setUp()
        self.currency = self.user_currencies[0]
        self.url = reverse("currencies:replace_currency", args=[self.currency.pk])

    def test_replace_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_invalid_form_display_errors(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "code", "To pole jest wymagane.")
        self.assertTemplateUsed(response, "currencies/replace_currency.html")

    def test_replace_currency_with_valid_data(self):
        self.client.login(username=self.user.email, password="test")

        currency_data = CurrencyDictFactory(code="USD")
        response = self.client.post(self.url, currency_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("currencies:list_currencies"))
        self.assertTrue(Currency.objects.filter(code="USD", user=self.user).exists())

    def test_return_404_if_not_my_currency(self):
        self.client.login(username=self.user.email, password="test")

        other_currency = CurrencyFactory()
        url = reverse("currencies:replace_currency", args=[other_currency.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_get_form(self):
        self.client.login(username=self.user.email, password="test")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)


class TestDeleteCurrency(TestCurrency):
    def setUp(self) -> None:
        super().setUp()
        self.currency = self.user_currencies[0]
        self.url = reverse("currencies:delete_currency", args=[self.currency.pk])

    def test_delete_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_delete_if_logged(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        with self.assertRaises(ObjectDoesNotExist):
            Currency.objects.get(pk=self.currency.pk)
        self.assertEqual(response.status_code, 302)

    def test_return_404_if_not_my_currency(self):
        self.client.login(username=self.user.email, password="test")

        other_currency = CurrencyFactory()
        url = reverse("currencies:delete_currency", args=[other_currency.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
