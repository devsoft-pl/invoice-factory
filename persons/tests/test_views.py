from django.test import TestCase
from django.urls import reverse
from parameterized import parameterized

from persons.factories import PersonFactory
from persons.models import Person
from users.factories import UserFactory


class TestPerson(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.set_password("test")
        self.user.save()
        self.user_persons = PersonFactory.create_batch(12, user=self.user)


class TestListPersons(TestPerson):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("persons:list_persons")

    def test_list_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_list_if_logged(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        object_list = response.context["persons"]

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "persons/list_persons.html")
        self.assertTrue(len(object_list) == 10)
        self.assertListEqual(
            list(object_list), list(Person.objects.filter(user=self.user)[:10])
        )

    def test_returns_first_page_when_abc(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(f"{self.url}?page=abc")

        object_list = response.context["persons"]

        self.assertEqual(
            list(object_list), list(Person.objects.filter(user=self.user)[:10])
        )

    @parameterized.expand([[2], [666]])
    def test_pagination_return_correct_list(self, page):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(f"{self.url}?page={page}")

        object_list = response.context["persons"]

        self.assertTrue(len(object_list) == 2)


class TestDetailPersons(TestPerson):
    def setUp(self) -> None:
        super().setUp()
        self.person = self.user_persons[0]
        self.url = reverse("persons:detail_person", args=[self.person.pk])

    def test_detail_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_detail_if_logged(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "persons/detail_person.html")
        self.assertEqual(self.person.pk, response.context["person"].pk)

    def test_return_404_if_not_my_person(self):
        self.client.login(username=self.user.email, password="test")

        self.other_person = PersonFactory()
        url = reverse("persons:detail_person", args=[self.other_person.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
