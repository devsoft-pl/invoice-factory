import pytest

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
        for field_name in form.Meta.fields:
            assert form.fields[field_name].widget.attrs["class"] == "form-control"


@pytest.mark.django_db
class TestUserForm:

    def test_form_fields_have_correct_class(self):
        form = UserForm()
        for field_name in form.Meta.fields:
            assert form.fields[field_name].widget.attrs["class"] == "form-control"
