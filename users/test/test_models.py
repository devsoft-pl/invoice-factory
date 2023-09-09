import pytest

from users.factories import UserFactory


@pytest.mark.django_db
class TestUserModel:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.user = UserFactory.create()

    def test_returns_full_name(self):
        assert (
            self.user.get_full_name() == f"{self.user.first_name} {self.user.last_name}"
        )

    def test_returns_short_name(self):
        assert self.user.get_short_name() == self.user.email
