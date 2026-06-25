import time

import pytest
from django.core.signing import TimestampSigner

from users.factories import UserFactory
from users.forms import (
    LoginUserForm,
    PasswordChangeUserForm,
    PasswordResetConfirmUserForm,
    PasswordResetUserForm,
    UserCreationForm,
    UserForm,
)


@pytest.mark.django_db
class TestPasswordResetUserForm:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.user = UserFactory.create()

    def test_form_fields_have_correct_class(self):
        form = PasswordResetUserForm()
        for field_name in form.Meta.fields:
            assert form.fields[field_name].widget.attrs["class"] == "form-control"


@pytest.mark.django_db
class TestPasswordResetConfirmUserForm:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.user = UserFactory.create()

    def test_form_fields_have_correct_class(self):
        form = PasswordResetConfirmUserForm(user=self.user)
        for field_name in form.Meta.fields:
            assert form.fields[field_name].widget.attrs["class"] == "form-control"


@pytest.mark.django_db
class TestLoginUserForm:

    def test_form_fields_have_correct_class(self):
        form = LoginUserForm()
        for field_name in form.Meta.fields:
            assert form.fields[field_name].widget.attrs["class"] == "form-control"


@pytest.mark.django_db
class TestPasswordChangeUserForm:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.user = UserFactory.create()

    def test_form_fields_have_correct_class(self):
        form = PasswordChangeUserForm(user=self.user)
        for field_name in form.Meta.fields:
            assert form.fields[field_name].widget.attrs["class"] == "form-control"


@pytest.mark.django_db
class TestUserCreationForm:

    def test_form_fields_have_correct_class(self):
        form = UserCreationForm()
        for field_name in ["email", "password1", "password2"]:
            assert form.fields[field_name].widget.attrs["class"] == "form-control"

    def test_valid_registration(self):
        timestamp = TimestampSigner().sign(str(time.time() - 5))  # 5 seconds ago
        form = UserCreationForm(
            data={
                "email": "test@test.pl",
                "password1": "Password123!",
                "password2": "Password123!",
                "timestamp": timestamp,
                "honeypot": "",
            }
        )
        assert form.is_valid()

    def test_honeypot_filled(self):
        timestamp = TimestampSigner().sign(str(time.time() - 5))
        form = UserCreationForm(
            data={
                "email": "test@test.pl",
                "password1": "Password123!",
                "password2": "Password123!",
                "timestamp": timestamp,
                "honeypot": "somebotvalue",
            }
        )
        assert not form.is_valid()
        assert "honeypot" not in form.errors
        assert "Registration not allowed for bots." in form.non_field_errors()

    def test_too_fast_registration(self):
        timestamp = TimestampSigner().sign(str(time.time() - 1))  # 1 second ago
        form = UserCreationForm(
            data={
                "email": "test@test.pl",
                "password1": "Password123!",
                "password2": "Password123!",
                "timestamp": timestamp,
                "honeypot": "",
            }
        )
        assert not form.is_valid()
        assert "Registration too fast, possible bot." in form.non_field_errors()


@pytest.mark.django_db
class TestUserForm:

    def test_form_fields_have_correct_class(self):
        form = UserForm()
        for field_name in form.Meta.fields:
            assert form.fields[field_name].widget.attrs["class"] == "form-control"
