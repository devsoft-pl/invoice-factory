from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from parameterized import parameterized

from countries.factories import CountryFactory
from persons.factories import PersonDictFactory, PersonFactory
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

        other_person = PersonFactory()
        url = reverse("persons:detail_person", args=[other_person.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)


class TestCreatePerson(TestPerson):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("persons:create_person")

    def test_create_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_invalid_form_display_errors(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "first_name", _("This field is required.")
        )
        self.assertFormError(
            response.context["form"], "last_name", _("This field is required.")
        )
        self.assertFormError(
            response.context["form"], "address", _("This field is required.")
        )
        self.assertFormError(
            response.context["form"], "zip_code", _("This field is required.")
        )
        self.assertFormError(
            response.context["form"], "city", _("This field is required.")
        )

    def test_create_with_valid_data(self):
        self.client.login(username=self.user.email, password="test")

        country = CountryFactory.create(user=self.user)
        data = PersonDictFactory(
            first_name="Jan",
            last_name="Kowalski",
            nip="123456789",
            pesel="83071415362",
            zip_code="01-453",
            city="Warszawa",
            country=country.pk,
            email="test@test.pl",
            phone_number="123456789",
        )

        persons_before_create = Person.objects.filter(
            first_name=data["first_name"],
            last_name=data["last_name"],
            nip=data["nip"],
            pesel=data["pesel"],
            address=data["address"],
            zip_code=data["zip_code"],
            city=data["city"],
            user=self.user,
        ).count()

        response = self.client.post(self.url, data=data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("persons:list_persons"))
        self.assertTrue(
            Person.objects.filter(
                first_name=data["first_name"],
                last_name=data["last_name"],
                address=data["address"],
                zip_code=data["zip_code"],
                city=data["city"],
                user=self.user,
            ).exists()
        )
        self.assertTrue(
            Person.objects.filter(
                first_name=data["first_name"],
                last_name=data["last_name"],
                nip=data["nip"],
                pesel=data["pesel"],
                address=data["address"],
                zip_code=data["zip_code"],
                city=data["city"],
                user=self.user,
            ).count(),
            persons_before_create + 1,
        )

    def test_get_form(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "persons/create_person.html")


class TestCreatePersonAjax(TestPerson):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("persons:create_person_ajax")

    def test_replace_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_invalid_form_display_errors(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.post(self.url, {})

        response_json = response.json()
        self.assertFalse(response_json["success"])
        self.assertEqual(
            response_json["errors"]["first_name"], [_("This field is required.")]
        )
        self.assertEqual(
            response_json["errors"]["last_name"], [_("This field is required.")]
        )
        self.assertEqual(
            response_json["errors"]["address"], [_("This field is required.")]
        )
        self.assertEqual(
            response_json["errors"]["zip_code"], [_("This field is required.")]
        )
        self.assertEqual(
            response_json["errors"]["city"], [_("This field is required.")]
        )
        self.assertEqual(
            response_json["errors"]["country"], [_("This field is required.")]
        )
        self.assertEqual(response.status_code, 200)

    def test_create_with_valid_data(self):
        self.client.login(username=self.user.email, password="test")

        country = CountryFactory.create(user=self.user)
        data = PersonDictFactory(
            first_name="Jan",
            last_name="Kowalski",
            nip="123456789",
            pesel="83071415362",
            zip_code="01-453",
            city="Warszawa",
            country=country.pk,
            email="test@test.pl",
            phone_number="123456789",
        )

        persons_before_create = Person.objects.filter(
            first_name=data["first_name"],
            last_name=data["last_name"],
            nip=data["nip"],
            pesel=data["pesel"],
            address=data["address"],
            zip_code=data["zip_code"],
            city=data["city"],
            user=self.user,
        ).count()

        response = self.client.post(self.url, data=data)

        response_json = response.json()
        self.assertTrue(response_json["success"])
        self.assertEqual(response_json["name"], "Jan Kowalski")
        self.assertTrue(
            Person.objects.filter(
                first_name=data["first_name"],
                last_name=data["last_name"],
                nip=data["nip"],
                pesel=data["pesel"],
                address=data["address"],
                zip_code=data["zip_code"],
                city=data["city"],
                user=self.user,
            ).count(),
            persons_before_create + 1,
        )

    def test_get_form(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "persons/create_person_ajax.html")


class TestReplacePerson(TestPerson):
    def setUp(self) -> None:
        super().setUp()
        self.person = self.user_persons[0]
        self.url = reverse("persons:replace_person", args=[self.person.pk])

    def test_replace_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_invalid_form_display_errors(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "first_name", _("This field is required.")
        )
        self.assertFormError(
            response.context["form"], "last_name", _("This field is required.")
        )
        self.assertFormError(
            response.context["form"], "address", _("This field is required.")
        )
        self.assertFormError(
            response.context["form"], "zip_code", _("This field is required.")
        )
        self.assertFormError(
            response.context["form"], "city", _("This field is required.")
        )

    def test_replace_with_valid_date(self):
        self.client.login(username=self.user.email, password="test")

        country = CountryFactory.create(user=self.user)
        data = PersonDictFactory(
            first_name="Jan",
            last_name="Kowalski",
            nip="123456789",
            pesel="83071415362",
            zip_code="01-453",
            city="Warszawa",
            country=country.pk,
            email="test@test.pl",
            phone_number="123456789",
        )

        response = self.client.post(self.url, data=data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("persons:list_persons"))
        self.assertTrue(
            Person.objects.filter(
                first_name=data["first_name"],
                last_name=data["last_name"],
                nip=data["nip"],
                pesel=data["pesel"],
                address=data["address"],
                zip_code=data["zip_code"],
                city=data["city"],
                user=self.user,
            ).exists()
        )

    def test_return_404_if_not_my_person(self):
        self.client.login(username=self.user.email, password="test")

        other_person = PersonFactory()
        url = reverse("persons:replace_person", args=[other_person.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_get_form(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "persons/replace_person.html")


class TestDeletePerson(TestPerson):
    def setUp(self) -> None:
        super().setUp()
        self.person = self.user_persons[0]
        self.url = reverse("persons:delete_person", args=[self.person.pk])

    def test_delete_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_delete_if_logged(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("persons:list_persons"))
        with self.assertRaises(ObjectDoesNotExist):
            Person.objects.get(pk=self.person.pk)

    def test_return_404_if_not_my_person(self):
        self.client.login(username=self.user.email, password="test")

        other_person = PersonFactory()
        url = reverse("persons:delete_person", args=[other_person.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
