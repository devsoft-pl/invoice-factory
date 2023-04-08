from rest_framework import serializers

from items.models import Item


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ["id", "name", "pkwiu", "amount", "net_price", "vat", "user"]
        extra_kwargs = {"id": {"read_only": False}}
