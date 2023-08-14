from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.urls import reverse

from countries.factories import CountryFactory
from countries.models import Country
from users.factories import UserFactory


class TestCountry(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.set_password("test")
        self.user.save()
        self.user_countries = CountryFactory.create_batch(12, user=self.user)
        self.other_country = CountryFactory()


class TestListCountries(TestCountry):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("countries:list_countries")

    def test_list_countries_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_list_countries(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(self.url)

        object_list = response.context["countries"]

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "countries/list_countries.html")
        self.assertTrue(len(object_list) == 10)
        self.assertListEqual(list(object_list), self.user_countries[:10])

    def test_list_countries_second_pag(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(f"{self.url}?page=2")

        object_list = response.context["countries"]

        self.assertTrue(len(object_list) == 2)
        self.assertListEqual(list(object_list), self.user_countries[10:])

    def test_returns_last_page_when_non_existent(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(f"{self.url}?page=666")

        object_list = response.context["countries"]

        self.assertListEqual(list(object_list), self.user_countries[10:])

    def test_returns_first_page_when_abc(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(f"{self.url}?page=abc")

        object_list = response.context["countries"]

        self.assertListEqual(list(object_list), self.user_countries[:10])


class TestDeleteCountry(TestCountry):
    def setUp(self) -> None:
        super().setUp()
        self.country = self.user_countries[0]
        self.url = reverse("countries:delete_country", args=[self.country.pk])

    def test_delete_country_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_delete_country(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(self.url)

        with self.assertRaises(ObjectDoesNotExist):
            Country.objects.get(pk=self.country.pk)
        self.assertEqual(response.status_code, 302)

    def test_return_404_if_not_my_countries(self):
        url = reverse("countries:delete_country", args=[self.other_country.pk])
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)


class TestCreateCountry(TestCountry):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("countries:create_country")

    def test_create_country_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_invalid_form_display_errors(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "country", "To pole jest wymagane."
        )
        self.assertTemplateUsed(response, "countries/create_country.html")

    def test_create_country_with_valid_data(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.post(self.url, {"country": "Polska"})

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("countries:list_countries"))
        self.assertTrue(
            Country.objects.filter(country="Polska", user=self.user).count(), 1
        )

    def test_create_country_with_valid_data_and_next(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.post(
            self.url, {"country": "Polska", "next": reverse("companies:create_company")}
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("companies:create_company"))
        self.assertTrue(
            Country.objects.filter(country="Polska", user=self.user).count(), 1
        )

    def test_get_form(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)


class TestReplaceCountry(TestCountry):
    def setUp(self) -> None:
        super().setUp()
        self.country = self.user_countries[0]
        self.url = reverse("countries:replace_country", args=[self.country.pk])

    def test_replace_country_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_return_404_if_not_my_countries(self):
        url = reverse("countries:replace_country", args=[self.other_country.pk])
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_invalid_form_display_errors(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "country", "To pole jest wymagane."
        )
        self.assertTemplateUsed(response, "countries/replace_country.html")

    def test_replace_country_with_valid_data(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.post(self.url, {"country": "Szwecja"})

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("countries:list_countries"))
        self.assertTrue(
            Country.objects.filter(country="Szwecja", user=self.user).exists()
        )

    def test_get_form(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
