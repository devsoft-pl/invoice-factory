from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from users.factories import UserFactory
from users.models import User


class TestUser(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.password = "test"
        self.user.set_password(self.password)
        self.user.save()


class TestDetailUser(TestUser):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("users:detail_user")

    def test_detail_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_detail_if_logged(self):
        self.client.login(username=self.user.email, password=self.password)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/detail_user.html")
        self.assertEqual(self.user.pk, response.context["user"].pk)


class TestReplaceUser(TestUser):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("users:replace_user")

    def test_replace_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_invalid_form_display_errors(self):
        self.client.login(username=self.user.email, password=self.password)

        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "email", _("This field is required.")
        )
        self.assertTemplateUsed(response, "registration/replace_user.html")

    def test_replace_with_valid_data(self):
        self.client.login(username=self.user.email, password=self.password)

        response = self.client.post(
            self.url,
            {
                "username": self.user.email,
                "first_name": "First name",
                "last_name": "Last name",
                "email": "test@test.pl",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("users:detail_user"))
        self.assertTrue(
            User.objects.filter(
                first_name="First name",
                last_name="Last name",
                email="test@test.pl",
                pk=self.user.pk,
            ).exists()
        )

    def test_get_form(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)


class TestRegisterUser(TestUser):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("users:register_user")

    def test_invalid_form_display_errors(self):
        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "email", _("This field is required.")
        )
        self.assertFormError(
            response.context["form"], "password1", _("This field is required.")
        )
        self.assertFormError(
            response.context["form"], "password2", _("This field is required.")
        )
        self.assertTemplateUsed(response, "registration/register.html")

    def test_register_with_valid_data(self):
        email = "test@test.pl"
        password = "Test_password1!"
        response = self.client.post(
            self.url,
            {"email": email, "password1": password, "password2": password},
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("index"))
        self.assertTrue(User.objects.filter(email="test@test.pl").exists())

    def test_get_form(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)


class TestPasswordChangeUser(TestUser):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("users:password_change_user")

    def test_invalid_form_display_errors(self):
        self.client.login(username=self.user.email, password=self.password)

        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "old_password", _("This field is required.")
        )
        self.assertFormError(
            response.context["form"], "new_password1", _("This field is required.")
        )
        self.assertFormError(
            response.context["form"], "new_password2", _("This field is required.")
        )
        self.assertTemplateUsed(response, "registration/password_change_user.html")

    def test_password_change_with_valid_data(self):
        self.client.login(username=self.user.email, password=self.password)

        new_password = "Test_new_password1!"
        response = self.client.post(
            self.url,
            {
                "username": self.user.email,
                "old_password": self.password,
                "new_password1": new_password,
                "new_password2": new_password,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("users:detail_user"))

        user = User.objects.get(email=self.user.email)

        self.assertTrue(user.check_password(new_password))

    def test_user_is_not_authenticated(self):
        response = self.client.get(self.url, fallow=True)

        self.assertEqual(response.status_code, 404)

    def test_get_form(self):
        self.client.login(username=self.user.email, password=self.password)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
