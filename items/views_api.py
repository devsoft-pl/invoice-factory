from rest_framework import viewsets

from items.models import Item
from items.serializers import ItemSerializer
from users.views_api import OwnedObjectsMixin


class ItemViewSet(OwnedObjectsMixin, viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
