from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.urls import reverse

from invoices.factories import InvoiceFactory
from items.factories import ItemFactory
from items.models import Item
from users.factories import UserFactory
from vat_rates.factories import VatRateFactory


class TestItem(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.set_password("test")
        self.user.save()
        self.user_items = ItemFactory.create_batch(
            12, user=self.user, invoice__user=self.user
        )
        self.other_item = ItemFactory()
        self.invoice = InvoiceFactory(user=self.user)
        self.vat = VatRateFactory(user=self.user)


class TestDeleteItem(TestItem):
    def setUp(self) -> None:
        super().setUp()
        self.item = self.user_items[0]
        self.url = reverse("items:delete_item", args=[self.item.pk])

    def test_delete_item_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_delete_country_if_logged(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(self.url)

        with self.assertRaises(ObjectDoesNotExist):
            Item.objects.get(pk=self.item.pk)
        self.assertEqual(response.status_code, 302)

    def rest_return_404_if_not_my_item(self):
        url = reverse("items:delete_item", args=[self.other_item.pk])
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)


class TestCreateItem(TestItem):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("items:create_item", args=[self.invoice.pk])

    def test_create_item_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_invalid_form_display_errors(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "name", "To pole jest wymagane.")
        self.assertFormError(
            response.context["form"], "net_price", "To pole jest wymagane."
        )
        self.assertFormError(response.context["form"], "vat", "To pole jest wymagane.")
        self.assertTemplateUsed(response, "items/create_item.html")

    def test_create_item_with_valid_data(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.post(
            self.url,
            {
                "name": "test",
                "pkwiu": "62.01.1",
                "amount": "1",
                "net_price": "12000",
                "vat": self.vat.pk,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse("invoices:detail_invoice", args=[self.invoice.pk])
        )
        self.assertTrue(
            Item.objects.filter(
                name="test",
                pkwiu="62.01.1",
                amount="1",
                net_price="12000",
                vat=self.vat.pk,
                user=self.user,
            ).exists()
        )
        self.assertEqual(
            Item.objects.filter(
                name="test",
                pkwiu="62.01.1",
                amount="1",
                net_price="12000",
                vat=self.vat.pk,
                user=self.user,
            ).count(),
            1,
        )

    def test_get_form(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)


class TestReplaceItem(TestItem):
    def setUp(self) -> None:
        super().setUp()
        self.item = self.user_items[0]
        self.url = reverse("items:replace_item", args=[self.item.pk])

    def test_replace_item_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def rest_return_404_if_not_my_item(self):
        url = reverse("items:replace_item", args=[self.other_item.pk])
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_invalid_form_display_errors(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "pkwiu", "To pole jest wymagane."
        )
        self.assertFormError(
            response.context["form"], "amount", "To pole jest wymagane."
        )
        self.assertFormError(response.context["form"], "vat", "To pole jest wymagane.")
        self.assertTemplateUsed(response, "items/replace_item.html")

    def test_replace_item_with_valid_data(self):
        self.client.login(username=self.user.username, password="test")

        response = self.client.post(
            self.url,
            {
                "name": "test2",
                "pkwiu": "62.01.1",
                "amount": "1",
                "net_price": "12000",
                "vat": self.vat.pk,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse("invoices:detail_invoice", args=[self.item.invoice.pk])
        )
        self.assertTrue(
            Item.objects.filter(
                name="test2",
                pkwiu="62.01.1",
                amount="1",
                net_price="12000",
                vat=self.vat.pk,
                user=self.user,
            ).exists()
        )
        self.assertEqual(
            Item.objects.filter(
                name="test2",
                pkwiu="62.01.1",
                amount="1",
                net_price="12000",
                vat=self.vat.pk,
                user=self.user,
            ).count(),
            1,
        )
