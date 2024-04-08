from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.urls import reverse
from parameterized import parameterized

from users.factories import UserFactory
from vat_rates.factories import VatRateFactory
from vat_rates.models import VatRate


class TestVatRate(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.set_password("test")
        self.user.save()
        self.user_rates = sorted(
            VatRateFactory.create_batch(12, user=self.user),
            key=lambda vat_rate: vat_rate.rate,
        )


class TestListVatRates(TestVatRate):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("vat_rates:list_vat_rates")

    def test_list_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_list_if_logged(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        object_list = response.context["vat_rates"]

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "vat_rates/list_vat_rates.html")
        self.assertTrue(len(object_list) == 10)
        self.assertListEqual(list(object_list), self.user_rates[:10])

    def test_returns_first_page_when_abc(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(f"{self.url}?page=abc")

        object_list = response.context["vat_rates"]

        self.assertListEqual(list(object_list), self.user_rates[:10])

    @parameterized.expand([[2], [666]])
    def test_pagination_return_correct_list(self, page):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(f"{self.url}?page={page}")

        object_list = response.context["vat_rates"]

        self.assertTrue(len(object_list) == 2)
        self.assertListEqual(list(object_list), self.user_rates[10:])


class TestCreateVatRate(TestVatRate):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("vat_rates:create_vat")

    def test_create_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_invalid_form_display_errors(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "rate", "To pole jest wymagane")

    def test_create_with_valid_data(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.post(self.url, {"rate": "23"})

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("vat_rates:list_vat_rates"))
        self.assertTrue(VatRate.objects.filter(rate="23", user=self.user).count(), 1)

    def test_get_form(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "vat_rates/create_vat.html")


class TestCreateVatRateAjax(TestVatRate):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("vat_rates:create_vat_ajax")

    def test_create_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_invalid_form_display_errors(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.post(self.url, {})

        response_json = response.json()
        self.assertFalse(response_json["success"])
        self.assertEqual(response_json["errors"]["rate"], ["To pole jest wymagane"])
        self.assertEqual(response.status_code, 200)

    def test_create_with_valid_data(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.post(self.url, {"rate": 99})

        response_json = response.json()
        self.assertTrue(response_json["success"])
        self.assertEqual(response_json["name"], 99)
        self.assertTrue(VatRate.objects.filter(rate=99, user=self.user).count(), 1)
        self.assertEqual(response.status_code, 200)

    def test_get_form(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 405)


class TestReplaceVatRate(TestVatRate):
    def setUp(self) -> None:
        super().setUp()
        self.vat_rate = self.user_rates[0]
        self.url = reverse("vat_rates:replace_vat", args=[self.vat_rate.pk])

    def test_replace_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_invalid_form_display_errors(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "rate", "To pole jest wymagane")

    def test_replace_with_valid_data(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.post(self.url, {"rate": "12"})

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("vat_rates:list_vat_rates"))
        self.assertTrue(VatRate.objects.filter(rate="12", user=self.user).exists())

    def test_return_404_if_not_my_vat_rate(self):
        self.client.login(username=self.user.email, password="test")

        other_rate = VatRateFactory()
        url = reverse("vat_rates:replace_vat", args=[other_rate.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_get_form(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "vat_rates/replace_vat.html")


class TestDeleteVatRate(TestVatRate):
    def setUp(self) -> None:
        super().setUp()
        self.vat_rate = self.user_rates[0]
        self.url = reverse("vat_rates:delete_vat", args=[self.vat_rate.pk])

    def test_delete_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_delete_if_logged(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        with self.assertRaises(ObjectDoesNotExist):
            VatRate.objects.get(pk=self.vat_rate.pk)
        self.assertEqual(response.status_code, 302)

    def test_return_404_if_not_my_vat_rate(self):
        self.client.login(username=self.user.email, password="test")

        other_rate = VatRateFactory()
        url = reverse("vat_rates:delete_vat", args=[other_rate.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
