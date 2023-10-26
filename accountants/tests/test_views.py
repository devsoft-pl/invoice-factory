from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.urls import reverse

from accountants.factories import AccountantFactory
from accountants.models import Accountant
from users.factories import UserFactory


class TestAccountant(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.set_password("test")
        self.user.save()
        self.user_accountants = AccountantFactory.create_batch(2, user=self.user)
        self.other_accountant = AccountantFactory()


class TestListAccountant(TestAccountant):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("accountants:list_accountants")

    def test_list_if_not_logged(self):
        response = self.client.get(self.url, fOllow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_list_if_logged(self):
        self.client.login(username=self.user.email, password="test")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accountants/list_accountants.html")


class TestDeleteAccountant(TestAccountant):
    def setUp(self) -> None:
        super().setUp()
        self.accountant = self.user_accountants[0]
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
        url = reverse("accountants:delete_accountant", args=[self.other_accountant.pk])
        self.client.login(username=self.user.email, password="test")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
