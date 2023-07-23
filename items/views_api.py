from rest_framework import viewsets

from base.mixins import OwnedObjectsMixin
from items.models import Item
from items.serializers import ItemSerializer


class ItemViewSet(OwnedObjectsMixin, viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
