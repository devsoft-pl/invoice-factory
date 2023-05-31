from django.test import TestCase
from django.urls import reverse

from users.factories import UserFactory
from vat_rates.factories import VatRateFactory


class TestVatRate(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.set_password("test")
        self.user.save()
        self.user_rates = sorted(
            VatRateFactory.create_batch(12, user=self.user),
            key=lambda vat_rate: vat_rate.rate,
        )
        self.other_rate = VatRateFactory()


class TestListVatRates(TestVatRate):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("vat_rates:list_vat_rates")

    def test_list_vat_rates_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_list_vat_rates_if_logged(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(self.url)

        object_list = response.context["vat_rates"]

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "vat_rates/list_vat_rates.html")
        self.assertTrue(len(object_list) == 10)
        self.assertListEqual(list(object_list), self.user_rates[:10])

    def test_list_vat_rates_second_pag(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(f"{self.url}?page=2")

        object_list = response.context["vat_rates"]

        self.assertTrue(len(object_list) == 2)
        self.assertListEqual(list(object_list), self.user_rates[10:])


class TestDeleteVatRate(TestVatRate):
    def setUp(self) -> None:
        super().setUp()
        self.vat_rate = self.user_rates[0]
        self.url = reverse("vat_rates:delete_vat", args=[self.vat_rate.pk])

    def test_delete_vat_rate_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_delete_vat_rate_if_logged(self):
        self.client.login(username=self.user.username, password="test")

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def rest_return_404_if_not_my_vat_rate(self):
        url = reverse("countries:delete_country", args=[self.other_rate.pk])
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
