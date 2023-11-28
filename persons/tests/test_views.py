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
        self.user_person = PersonFactory.create_batch(12, user=self.user)
        self.other_person = PersonFactory()


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
