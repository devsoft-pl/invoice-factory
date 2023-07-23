from unittest.mock import Mock

import pytest

from users.factories import UserFactory
from users.views_api import UserViewSet


@pytest.mark.django_db
class TestUserViewSet:
    @pytest.fixture(autouse=True)
    def set_up(self):
        self.superuser = UserFactory(is_superuser=True)
        self.user = UserFactory()
        self.user_view = UserViewSet()

    def test_get_queryset_if_superuser(self):
        self.user_view.request = Mock(user=self.superuser)

        assert self.user_view.get_queryset().count() == 2

    def test_get_queryset_if_user(self):
        self.user_view.request = Mock(user=self.user)

        assert self.user_view.get_queryset().count() == 1
