from django.test import TestCase
from django.urls import reverse

from currencies.factories import CurrencyFactory
from users.factories import UserFactory


class TestCurrency(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.set_password("test")
        self.user.save()
        self.user_currencies = CurrencyFactory.create_batch(12, user=self.user)
        self.user_currency = CurrencyFactory()

    def test_list_currencies_if_not_logged(self):
        url = reverse("currencies:list_currencies")
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, "/users/login/?next=/currencies/")

    def test_list_currencies_if_logged(self):
        url = reverse("currencies:list_currencies")
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(url)

        object_list = response.context["currencies"]

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "currencies/list_currencies.html")
        self.assertTrue(len(object_list) == 10)
        self.assertListEqual(list(object_list), self.user_currencies[:10])

    def test_list_currencies_second_pag(self):
        url = reverse("currencies:list_currencies")
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(f"{url}?page=2")

        object_list = response.context["currencies"]

        self.assertTrue(len(object_list) == 2)
        self.assertListEqual(list(object_list), self.user_currencies[10:])
