import pytest

from persons.factories import PersonFactory


@pytest.mark.django_db
class TestPersonModel:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.person = PersonFactory.create()

    def test_returns_full_name(self):
        assert (
            self.person.full_name == f"{self.person.first_name} {self.person.last_name}"
        )

    def test_returns_str_full_name(self):
        assert (
            self.person.__str__() == f"{self.person.first_name} {self.person.last_name}"
        )
