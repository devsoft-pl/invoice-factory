import pytest

from users.factories import UserDictFactory
from users.serializers import UserSerializer


@pytest.mark.django_db
class TestUserSerializer:
    @pytest.fixture(autouse=True)
    def set_up(self):
        self.user_data = UserDictFactory()

    def test_create_user_if_valid_data(self):
        serializer = UserSerializer()
        user = serializer.create(self.user_data)

        assert user.email == self.user_data["email"]
        assert user.pk
        assert user.auth_token
