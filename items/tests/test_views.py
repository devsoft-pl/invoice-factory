from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.urls import reverse

from invoices.factories import InvoiceSellFactory
from items.factories import ItemDictFactory, ItemFactory
from items.models import Item
from users.factories import UserFactory
from vat_rates.factories import VatRateFactory


class TestItem(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.set_password("test")
        self.user.save()

        self.invoice = InvoiceSellFactory(user=self.user)
        self.vat = VatRateFactory(user=self.user)
        self.user_items = ItemFactory.create_batch(
            12, invoice=self.invoice, vat=self.vat
        )
        self.other_item = ItemFactory()


class TestCreateItem(TestItem):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("items:create_item", args=[self.invoice.pk])

    def test_create_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_invalid_form_display_errors(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "name", "To pole jest wymagane.")
        self.assertFormError(
            response.context["form"], "net_price", "To pole jest wymagane."
        )
        self.assertFormError(response.context["form"], "vat", "To pole jest wymagane.")
        self.assertTemplateUsed(response, "items/create_item.html")

    def test_create_with_valid_data(self):
        self.client.login(username=self.user.email, password="test")

        item_date = ItemDictFactory(vat=self.vat.pk)
        response = self.client.post(self.url, item_date)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse("invoices:detail_invoice", args=[self.invoice.pk])
        )
        self.assertTrue(
            Item.objects.filter(
                name=item_date["name"], pkwiu=item_date["pkwiu"]
            ).exists()
        )

    def test_get_form(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)


class TestReplaceItem(TestItem):
    def setUp(self) -> None:
        super().setUp()
        self.item = self.user_items[0]
        self.url = reverse("items:replace_item", args=[self.item.pk])

    def test_replace_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_invalid_form_display_errors(self):
        self.client.login(username=self.user.email, password="test")

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

    def test_replace_with_valid_data(self):
        self.client.login(username=self.user.email, password="test")

        item_date = ItemDictFactory(vat=self.vat.pk)
        response = self.client.post(self.url, item_date)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse("invoices:detail_invoice", args=[self.item.invoice.pk])
        )
        self.assertTrue(
            Item.objects.filter(
                name=item_date["name"], pkwiu=item_date["pkwiu"]
            ).exists()
        )

    def test_return_404_if_not_my_item(self):
        self.client.login(username=self.user.email, password="test")

        url = reverse("items:replace_item", args=[self.other_item.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_get_form(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)


class TestDeleteItem(TestItem):
    def setUp(self) -> None:
        super().setUp()
        self.item = self.user_items[0]
        self.url = reverse("items:delete_item", args=[self.item.pk])

    def test_delete_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_delete_if_logged(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        with self.assertRaises(ObjectDoesNotExist):
            Item.objects.get(pk=self.item.pk)
        self.assertEqual(response.status_code, 302)

    def test_return_404_if_not_my_item(self):
        self.client.login(username=self.user.email, password="test")

        url = reverse("items:delete_item", args=[self.other_item.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
