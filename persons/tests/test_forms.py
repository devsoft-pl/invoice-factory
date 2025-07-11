import pytest

from countries.factories import CountryFactory
from countries.models import Country
from persons.factories import PersonDictFactory, PersonFactory
from persons.forms import PersonFilterForm, PersonForm
from persons.models import Person
from users.factories import UserFactory


@pytest.mark.django_db
class TestPersonForm:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.user = UserFactory.create()
        self.country = CountryFactory.create(user=self.user)
        self.person_1 = PersonFactory.create(
            first_name="Mateusz",
            last_name="Maciejewski",
            nip="123456789",
            pesel="83071415362",
            address="Makowa 1",
            zip_code="01-234",
            city="Warszawa",
            country=self.country,
            email="test@test.pl",
            phone_number="111111111",
            user=self.user,
        )
        self.person_2 = PersonFactory.create(
            first_name="Orfeusz",
            last_name="Tomaszewski",
            nip="987654321",
            pesel="85081515363",
            address="Skokowa 3",
            zip_code="05-678",
            city="Wrocław",
            country=self.country,
            email="test2@test.pl",
            phone_number="222222222",
            user=self.user,
        )

    @pytest.mark.parametrize(
        "person_last_name, expected_count",
        [["Mac", 1], ["Maciejewski", 1], ["wski", 2]],
    )
    def test_return_filtered_with_different_parts_of_person_last_name(
        self, person_last_name, expected_count
    ):
        request_get = {"last_name": person_last_name}

        self.form = PersonFilterForm(request_get)
        self.form.is_valid()

        persons_list = Person.objects.filter(user=self.user)
        filtered_list = self.form.get_filtered_persons(persons_list)

        assert self.person_1.id == filtered_list[0].id
        assert filtered_list.count() == expected_count

    def test_return_filtered_empty_list_when_person_last_name_not_exist(self):
        request_get = {"last_name": "Kowalski"}

        self.form = PersonFilterForm(request_get)
        self.form.is_valid()

        persons_list = Person.objects.filter(user=self.user)
        filtered_list = self.form.get_filtered_persons(persons_list)

        assert filtered_list.count() == 0

    @pytest.mark.parametrize(
        "person_first_name, expected_count", [["Mat", 1], ["Mateusz", 1], ["eusz", 2]]
    )
    def test_return_filtered_with_different_parts_of_person_first_name(
        self, person_first_name, expected_count
    ):
        request_get = {"first_name": person_first_name}

        self.form = PersonFilterForm(request_get)
        self.form.is_valid()

        persons_list = Person.objects.filter(user=self.user)
        filtered_list = self.form.get_filtered_persons(persons_list)

        assert self.person_1.id == filtered_list[0].id
        assert filtered_list.count() == expected_count

    def test_return_filtered_empty_list_when_person_first_name_not_exist(self):
        request_get = {"first_name": "Anna"}

        self.form = PersonFilterForm(request_get)
        self.form.is_valid()

        persons_list = Person.objects.filter(user=self.user)
        filtered_list = self.form.get_filtered_persons(persons_list)

        assert filtered_list.count() == 0

    @pytest.mark.parametrize(
        "person_address, expected_count", [["Mak", 1], ["Makowa", 1], ["kowa", 2]]
    )
    def test_return_filtered_with_different_parts_of_person_address(
        self, person_address, expected_count
    ):
        request_get = {"address": person_address}

        self.form = PersonFilterForm(request_get)
        self.form.is_valid()

        persons_list = Person.objects.filter(user=self.user)
        filtered_list = self.form.get_filtered_persons(persons_list)

        assert self.person_1.id == filtered_list[0].id
        assert filtered_list.count() == expected_count

    def test_return_filtered_empty_list_when_person_address_not_exist(self):
        request_get = {"address": "Topolowa"}

        self.form = PersonFilterForm(request_get)
        self.form.is_valid()

        persons_list = Person.objects.filter(user=self.user)
        filtered_list = self.form.get_filtered_persons(persons_list)

        assert filtered_list.count() == 0

    def test_form_with_valid_data(self):
        data = PersonDictFactory(
            first_name="Jan",
            last_name="Kowalski",
            nip="",
            pesel="",
            zip_code="01-450",
            city="Warszawa",
            country=self.country,
            email="test@test.pl",
            phone_number="123456789",
        )
        form = PersonForm(data=data, current_user=self.user)

        is_valid = form.is_valid()

        assert form.errors == {}
        assert is_valid

    def test_form_with_not_valid_data(self):
        data = PersonDictFactory(country=self.country)
        form = PersonForm(data=data, current_user=self.user)
        is_valid = form.is_valid()

        assert form.errors == {
            "nip": [
                "Pleas enter a tax ID with a minimum of 8 characters and no special characters"
            ],
            "pesel": ["Please enter Pesel with 11 numbers"],
            "zip_code": [
                "Please enter the zip code with a numbers in the format xx-xxx"
            ],
            "phone_number": ["Please enter a phone with a minimum 9 numbers"],
        }
        assert not is_valid

    def test_form_with_person_already_exists(self):
        data = PersonDictFactory(
            pesel=self.person_1.pesel,
            nip=self.person_1.nip,
            zip_code="01-450",
            phone_number="111111112",
            country=self.country,
        )
        form = PersonForm(data=data, current_user=self.user)
        is_valid = form.is_valid()

        assert form.errors == {
            "nip": ["Nip already exists"],
            "pesel": ["Pesel already exists"],
        }
        assert not is_valid

    def test_form_with_person_data_already_exists(self):
        data = PersonDictFactory(
            first_name=self.person_1.first_name,
            last_name=self.person_1.last_name,
            address=self.person_1.address,
            zip_code=self.person_1.zip_code,
            city=self.person_1.city,
            pesel=85081515178,
            nip=1234567890,
            phone_number=555555555,
            country=self.country,
        )
        form = PersonForm(data=data, current_user=self.user)
        is_valid = form.is_valid()

        assert form.errors == {
            "__all__": ["Person with given data already exists"],
        }
        assert not is_valid

    def test_filtered_countries_current_user(self):
        self.form = PersonForm(current_user=self.user)
        form_countries_ids = self.form.fields["country"].queryset.values_list(
            "id", flat=True
        )
        user_countries_ids = Country.objects.filter(user=self.user).values_list(
            "id", flat=True
        )

        assert set(form_countries_ids) == set(user_countries_ids)
        assert form_countries_ids.count() == user_countries_ids.count()
