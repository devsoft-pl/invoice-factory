from unittest.mock import Mock, patch

import pytest

from users.factories import UserFactory
from users.managers import UserManager


@pytest.mark.django_db
class TestUserManager:
    @patch("users.managers.UserManager._create_user")
    def test_returns_created_user(self, _create_user_mock):
        self.user = UserFactory()
        _create_user_mock.return_value = self.user

        assert UserManager().create_user(email=self.user.email) == self.user

    @patch("users.managers.UserManager._create_user")
    def test_returns_created_superuser(self, _create_user_mock):
        self.superuser = UserFactory(is_superuser=True, is_staff=True)
        _create_user_mock.return_value = self.superuser

        assert (
            UserManager().create_superuser(email=self.superuser.email) == self.superuser
        )

    @pytest.mark.parametrize(
        "is_staff, is_superuser", [[False, False], [True, False], [False, True]]
    )
    def test_returns_raise_when_create_superuser_if_staff_and_superuser_is_false(
        self, is_staff, is_superuser
    ):
        user = UserFactory()

        with pytest.raises(ValueError):
            UserManager().create_superuser(
                email=user.email, is_staff=is_staff, is_superuser=is_superuser
            )
