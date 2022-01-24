from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator

from invoices.models import (
    VatRate,
    Currency,
    Company,
    Invoice,
    Item,
)
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'password', 'email']
        extra_kwargs = {
            'password': {'required': True, 'write_only': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True, 'validators': [UniqueValidator(queryset=User.objects.all())]}
        }

    def create(self, validated_data):
        """Create user nad token"""
        user = User.objects.create_user(**validated_data)
        Token.objects.create(user=user)
        return user


class VatRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VatRate
        fields = ('id', 'rate', 'user')
        extra_kwargs = {
            'code': {'validators': []},
        }


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ('id', 'code', 'user')
        extra_kwargs = {
            'code': {'validators': []},
        }


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'nip', 'address', 'zip_code', 'city', 'email', 'phone_number', 'user']


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'unit', 'amount', 'net_price', 'vat', 'user']
        extra_kwargs = {'id': {'read_only': False}}  # zmieniamy na "nie tylko do odczytu" bo musimy miec id w PUT/PATCH


class InvoiceSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True)  # FK i many=True, wiec create

    class Meta:
        model = Invoice
        fields = ['company', 'invoice_type', 'payment_method', 'create_date', 'sale_date', 'payment_date',
                  'account_number', 'invoice_number', 'invoice_pdf', 'currency', 'items', 'user']

    def create(self, validated_data):
        items = validated_data.pop('items')
        invoice = Invoice.objects.create(**validated_data)

        for item in items:
            name = item['name']
            unit = item['unit']
            amount = item['amount']
            net_price = item['net_price']
            vat = item['vat']
            Item.objects.create(name=name, unit=unit, amount=amount, net_price=net_price, vat=vat, invoice=invoice)

        return invoice

    def update(self, instance: Invoice, validated_data):
        items = validated_data.pop('items', [])  # items jeśli jest to zdejmuje sie z validated_data, w innym ustawia []

        for key, values in validated_data.items():
            setattr(instance, key, values)  # ustawia wartosc atrybutu na instance
            # instance.currency = validated_data.get('currency') itd w całej instance

        """
        items = [
        {"id": 3, "name": "usluga sprzatająca", "unit": 4, "amount": 1, "net_price": 5000, "vat": 1},
        {"id": 4, "name": "usluga sprzedająca", "unit": 4, "amount": 1, "net_price": 3000, "vat": 1},
        ]
        """
        for item in items:
            item_id = item.pop('id')  # item.pop('id') = item['id'], zdejmuje id, bo nie można edytować id
            instance_item = Item.objects.get(pk=item_id)

            for key, values in item.items():
                setattr(instance_item, key, values)

            instance_item.save()

        instance.save()
        return instance






















