from unittest.mock import patch

import pytest

from users.factories import UserFactory
from users.managers import UserManager


@pytest.mark.django_db
class TestUserManager:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.user = UserFactory.create()

    @patch("users.managers.UserManager._create_user")
    def test_returns_created_user(self, _create_user_mock):
        _create_user_mock.return_value = self.user

        assert UserManager().create_user(email=self.user.email) == self.user

    @patch("users.managers.UserManager._create_user")
    def test_returns_created_superuser(self, _create_user_mock):
        superuser = UserFactory(is_superuser=True, is_staff=True)
        _create_user_mock.return_value = superuser

        assert UserManager().create_superuser(email=superuser.email) == superuser

    @pytest.mark.parametrize(
        "is_staff, is_superuser", [[False, False], [True, False], [False, True]]
    )
    def test_returns_raise_when_create_superuser_if_staff_and_superuser_is_false(
        self, is_staff, is_superuser
    ):
        with pytest.raises(ValueError):
            UserManager().create_superuser(
                email=self.user.email, is_staff=is_staff, is_superuser=is_superuser
            )
