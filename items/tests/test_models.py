import pytest

from items.factories import ItemFactory


@pytest.mark.django_db
class TestItemModel:
    @pytest.fixture(autouse=True)
    def set_up(self):
        self.item = ItemFactory.create()

    def test_str_returns_item_name(self):
        assert self.item.__str__() == self.item.name
