from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from users.factories import UserFactory


class TestUser(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.set_password("test")
        self.user.save()


class TestDetailUser(TestUser):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("users:detail_user")

    def test_detail_user_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_detail_user_if_logged(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/detail_user.html")
        self.assertEqual(self.user.pk, response.context["user"].pk)


class TestReplaceUser(TestUser):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("users:replace_user")

    def test_replace_user_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_invalid_form_display_errors(self):
        self.client.login(username=self.user.username, password="test")

        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "username", "To pole jest wymagane."
        )
        self.assertTemplateUsed(response, "registration/replace_user.html")

    def test_replace_user_with_valid_data(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.post(
            self.url, {"username": self.user.username, "email": "test@test.pl"}
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("users:detail_user"))
        self.assertTrue(
            User.objects.filter(email="test@test.pl", pk=self.user.pk).exists()
        )


class TestRegisterUser(TestUser):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("users:register_user")

    def test_invalid_form_display_errors(self):
        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "username", "To pole jest wymagane."
        )
        self.assertFormError(
            response.context["form"], "password1", "To pole jest wymagane."
        )
        self.assertFormError(
            response.context["form"], "password2", "To pole jest wymagane."
        )
        self.assertTemplateUsed(response, "registration/register.html")

    def test_register_user_with_valid_data(self):
        username = "User_test_1"
        password = "Test_password1!"
        response = self.client.post(
            self.url,
            {"username": username, "password1": password, "password2": password},
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("invoices:index"))
        self.assertTrue(User.objects.filter(username="User_test_1").exists())
