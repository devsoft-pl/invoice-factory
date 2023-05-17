from rest_framework import serializers

from items.models import Item


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = [
            "id",
            "invoice",
            "name",
            "pkwiu",
            "amount",
            "net_price",
            "vat",
            "user",
            "is_my_item",
        ]
        extra_kwargs = {"id": {"read_only": False}}
