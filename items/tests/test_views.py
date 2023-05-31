from django.test import TestCase
from django.urls import reverse

from items.factories import ItemFactory
from users.factories import UserFactory


class TestItem(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.set_password("test")
        self.user.save()
        self.user_items = ItemFactory.create_batch(12, user=self.user)
        self.other_item = ItemFactory()


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
        self.assertEqual(response.status_code, 302)

    def rest_return_404_if_not_my_item(self):
        url = reverse("items:delete_item", args=[self.other_item.pk])
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
