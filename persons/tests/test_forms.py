import pytest

from countries.factories import CountryFactory
from countries.models import Country
from persons.factories import PersonDictFactory, PersonFactory
from persons.forms import PersonFilterForm, PersonForm
from persons.models import Person
from users.factories import UserFactory


@pytest.mark.django_db
class TestPersonFilterForm:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.user = UserFactory.create()
        self.country = CountryFactory.create(user=self.user)
        self.person_1 = PersonFactory.create(
            first_name="Mateusz",
            last_name="Maciejewski",
            address="Makowa 1",
            user=self.user,
        )
        self.person_2 = PersonFactory.create(
            first_name="Orfeusz",
            last_name="Tomaszewski",
            address="Skokowa 3",
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


@pytest.mark.django_db
class TestPersonFormValidation:
    @pytest.fixture
    def user(self):
        return UserFactory()

    @pytest.fixture
    def polish_country(self, user):
        return CountryFactory(country="Polska", user=user)

    @pytest.fixture
    def foreign_country(self, user):
        return CountryFactory(country="Germany", user=user)

    def test_valid_polish_person_form(self, user, polish_country):
        data = PersonDictFactory(
            country=polish_country.pk,
            nip="1234567890",
            zip_code="12-345",
            pesel="83071415362",
            phone_number="123456789",
        )
        form = PersonForm(data=data, current_user=user)
        assert form.is_valid(), form.errors

    def test_invalid_polish_nip_in_form(self, user, polish_country):
        data = PersonDictFactory(country=polish_country.pk, nip="123")
        form = PersonForm(data=data, current_user=user)
        assert not form.is_valid()
        assert "nip" in form.errors
        assert "Polish NIP must consist of 10 digits." in form.errors["nip"][0]

    def test_invalid_polish_zip_code_in_form(self, user, polish_country):
        data = PersonDictFactory(country=polish_country.pk, zip_code="12345")
        form = PersonForm(data=data, current_user=user)
        assert not form.is_valid()
        assert "zip_code" in form.errors
        assert (
            "Polish ZIP code must be in the format XX-XXX."
            in form.errors["zip_code"][0]
        )

    def test_valid_foreign_person_form(self, user, foreign_country):
        data = PersonDictFactory(
            country=foreign_country.pk,
            nip="DE123456",
            zip_code="D-12345",
            pesel="83071415362",
            phone_number="123456789",
        )
        form = PersonForm(data=data, current_user=user)
        assert form.is_valid(), form.errors

    def test_invalid_foreign_nip_in_form(self, user, foreign_country):
        data = PersonDictFactory(country=foreign_country.pk, nip="DE123!@#")
        form = PersonForm(data=data, current_user=user)
        assert not form.is_valid()
        assert "nip" in form.errors
        assert (
            "Foreign VAT number contains invalid characters or is incorrect length."
            in form.errors["nip"][0]
        )

    def test_clean_nip_returns_error(self, user, polish_country):
        existing_person = PersonFactory(user=user, nip="1111111111")
        data = PersonDictFactory(country=polish_country.pk, nip=existing_person.nip)
        form = PersonForm(data=data, current_user=user)
        assert not form.is_valid()
        assert "nip" in form.errors
        assert "Nip already exists" in form.errors["nip"]

    def test_clean_pesel_returns_error(self, user, polish_country):
        existing_person = PersonFactory(user=user, pesel="83071415362")
        data = PersonDictFactory(country=polish_country.pk, pesel=existing_person.pesel)
        form = PersonForm(data=data, current_user=user)
        assert not form.is_valid()
        assert "pesel" in form.errors
        assert "Pesel already exists" in form.errors["pesel"]

    def test_form_with_person_data_already_exists(self, user, polish_country):
        existing_person = PersonFactory(user=user)
        data = PersonDictFactory(
            first_name=existing_person.first_name,
            last_name=existing_person.last_name,
            address=existing_person.address,
            zip_code=existing_person.zip_code,
            city=existing_person.city,
            country=polish_country.pk,
            pesel="83071415362",
            phone_number="123456789",
        )
        form = PersonForm(data=data, current_user=user)
        assert not form.is_valid()
        assert "__all__" in form.errors
        assert "Person with given data already exists" in form.errors["__all__"]

    def test_filtered_countries_current_user(self, user):
        CountryFactory(user=user)
        CountryFactory()  # Another user's country
        form = PersonForm(current_user=user)
        form_countries_ids = form.fields["country"].queryset.values_list(
            "id", flat=True
        )
        user_countries_ids = Country.objects.filter(user=user).values_list(
            "id", flat=True
        )
        assert set(form_countries_ids) == set(user_countries_ids)
        assert form_countries_ids.count() == 1
