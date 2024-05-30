from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.urls import reverse
from parameterized import parameterized

from countries.factories import CountryDictFactory, CountryFactory
from countries.models import Country
from users.factories import UserFactory


class TestCountry(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.set_password("test")
        self.user.save()
        CountryFactory.create_batch(12, user=self.user)
        self.user_countries = list(Country.objects.filter(user=self.user))


class TestListCountries(TestCountry):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("countries:list_countries")

    def test_list_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_list_if_logged(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        object_list = response.context["countries"]

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "countries/list_countries.html")
        self.assertTrue(len(object_list) == 10)
        self.assertListEqual(list(object_list), self.user_countries[:10])

    def test_returns_first_page_when_abc(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(f"{self.url}?page=abc")

        object_list = response.context["countries"]

        self.assertListEqual(list(object_list), self.user_countries[:10])

    @parameterized.expand([[2], [666]])
    def test_pagination_return_correct_list(self, page):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(f"{self.url}?page={page}")

        object_list = response.context["countries"]

        self.assertTrue(len(object_list) == 2)
        self.assertListEqual(list(object_list), self.user_countries[-2:])


class TestCreateCountry(TestCountry):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("countries:create_country")

    def test_create_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_create_invalid_form_display_errors(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "country", "This field is required."
        )

    def test_create_with_valid_data(self):
        self.client.login(username=self.user.email, password="test")

        country_data = CountryDictFactory(country="Polska")

        response = self.client.post(self.url, country_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("countries:list_countries"))
        self.assertTrue(
            Country.objects.filter(
                country=country_data["country"], user=self.user
            ).count(),
            1,
        )

    def test_get_form(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "countries/create_country.html")


class TestCreateCountryAjax(TestCountry):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("countries:create_country_ajax")

    def test_create_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_create_invalid_form_display_errors(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.post(self.url, {})

        response_json = response.json()
        self.assertFalse(response_json["success"])
        self.assertEqual(
            response_json["errors"]["country"], ["This field is required."]
        )
        self.assertEqual(response.status_code, 200)

    def test_create_with_valid_data(self):
        self.client.login(username=self.user.email, password="test")

        country_data = CountryDictFactory(country="polska")

        response = self.client.post(self.url, country_data)

        response_json = response.json()
        self.assertTrue(response_json["success"])
        self.assertEqual(response_json["name"], "Polska")
        self.assertTrue(
            Country.objects.filter(
                country=country_data["country"], user=self.user
            ).count(),
            1,
        )
        self.assertEqual(response.status_code, 200)

    def test_get_form(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 405)


class TestReplaceCountry(TestCountry):
    def setUp(self) -> None:
        super().setUp()
        self.country = self.user_countries[0]
        self.url = reverse("countries:replace_country", args=[self.country.pk])

    def test_replace_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_replace_invalid_form_display_errors(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "country", "This field is required."
        )

    def test_replace_with_valid_data(self):
        self.client.login(username=self.user.email, password="test")

        country_data = CountryDictFactory(country="Szwecja")

        response = self.client.post(self.url, country_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("countries:list_countries"))
        self.assertTrue(
            Country.objects.filter(
                country=country_data["country"], user=self.user
            ).exists()
        )

    def test_return_404_if_not_my_countries(self):
        self.client.login(username=self.user.email, password="test")

        other_country = CountryFactory()
        url = reverse("countries:replace_country", args=[other_country.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_get_form(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "countries/replace_country.html")


class TestDeleteCountry(TestCountry):
    def setUp(self) -> None:
        super().setUp()
        self.country = self.user_countries[0]
        self.url = reverse("countries:delete_country", args=[self.country.pk])

    def test_delete_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_delete_if_logged(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        with self.assertRaises(ObjectDoesNotExist):
            Country.objects.get(pk=self.country.pk)
        self.assertEqual(response.status_code, 302)

    def test_return_404_if_not_my_countries(self):
        self.client.login(username=self.user.email, password="test")

        other_country = CountryFactory()
        url = reverse("countries:delete_country", args=[other_country.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
