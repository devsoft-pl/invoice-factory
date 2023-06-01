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

    def test_list_countries_if_logged(self):
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


class TestDeleteCountry(TestCountry):
    def setUp(self) -> None:
        super().setUp()
        self.country = self.user_countries[0]
        self.url = reverse("countries:delete_country", args=[self.country.pk])

    def test_delete_country_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_delete_country_if_logged(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(self.url)

        with self.assertRaises(ObjectDoesNotExist):
            Country.objects.get(pk=self.country.pk)
        self.assertEqual(response.status_code, 302)

    def rest_return_404_if_not_my_countries(self):
        url = reverse("countries:delete_country", args=[self.other_country.pk])
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    # def test_call_view_fail_blank(self):
    #     self.client.login(username='user', password='test')
    #     response = self.client.post('/url/to/view', {}) # blank data dictionary
    #     self.assertFormError(response, 'form', 'some_field', 'This field is required.')
    #     # etc. ...
    #
    # def test_call_view_fail_invalid(self):
    #     # as above, but with invalid rather than blank data in dictionary
    #
    # def test_call_view_success_invalid(self):
    #     # same again, but with valid data, then
    #     self.assertRedirects(response, '/contact/1/calls/')
