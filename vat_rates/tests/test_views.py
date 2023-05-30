from django.test import TestCase
from django.urls import reverse

from currencies.factories import CurrencyFactory
from users.factories import UserFactory
from vat_rates.factories import VatRateFactory


class TestCurrency(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.set_password("test")
        self.user.save()
        self.user_rates = sorted(
            VatRateFactory.create_batch(12, user=self.user),
            key=lambda vat_rate: vat_rate.rate,
        )
        self.user_rate = VatRateFactory()

    def test_list_vates_if_not_logged(self):
        url = reverse("vat_rates:list_vates")
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, "/users/login/?next=/vat_rates/")

    def test_list_vates_if_logged(self):
        url = reverse("vat_rates:list_vates")
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(url)

        object_list = response.context["vat_rates"]

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "vat_rates/list_vates.html")
        self.assertTrue(len(object_list) == 10)
        self.assertListEqual(list(object_list), self.user_rates[:10])

    def test_list_vates_second_pag(self):
        url = reverse("vat_rates:list_vates")
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(f"{url}?page=2")

        object_list = response.context["vat_rates"]

        self.assertTrue(len(object_list) == 2)
        self.assertListEqual(list(object_list), self.user_rates[10:])
