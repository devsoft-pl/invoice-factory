from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator

from invoices.models import Invoice, Item


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "password", "email"]
        extra_kwargs = {
            "password": {"required": True, "write_only": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
            "email": {
                "required": True,
                "validators": [UniqueValidator(queryset=User.objects.all())],
            },
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        Token.objects.create(user=user)
        return user


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ["id", "name", "pkwiu", "amount", "net_price", "vat", "user"]
        extra_kwargs = {"id": {"read_only": False}}


class InvoiceSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True)

    class Meta:
        model = Invoice
        fields = [
            "company",
            "invoice_type",
            "payment_method",
            "create_date",
            "sale_date",
            "payment_date",
            "account_number",
            "invoice_number",
            "invoice_pdf",
            "currency",
            "items",
            "user",
        ]

    def create(self, validated_data):
        items = validated_data.pop("items")
        invoice = Invoice.objects.create(**validated_data)

        for item in items:
            name = item["name"]
            pkwiu = item["pkwiu"]
            amount = item["amount"]
            net_price = item["net_price"]
            vat = item["vat"]
            Item.objects.create(
                name=name,
                amount=amount,
                pkwiu=pkwiu,
                net_price=net_price,
                vat=vat,
                invoice=invoice,
            )

        return invoice

    def update(self, instance: Invoice, validated_data):
        items = validated_data.pop("items", [])

        for key, values in validated_data.items():
            setattr(instance, key, values)

        for item in items:
            item_id = item.pop("id")
            instance_item = Item.objects.get(pk=item_id)

            for key, values in item.items():
                setattr(instance_item, key, values)

            instance_item.save()

        instance.save()
        return instance
