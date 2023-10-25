import pytest

from accountants.factories import AccountantFactory


@pytest.mark.django_db
class TestAccountantModel:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.accountant = AccountantFactory.create()

    def test_returns_str_name(self):
        assert self.accountant.__str__() == self.accountant.name
