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
        fields = ('id', 'rate')
        extra_kwargs = {
            'code': {'validators': []},
        }


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ('id', 'code')
        extra_kwargs = {
            'code': {'validators': []},
        }


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'nip', 'address', 'zip_code', 'city', 'email', 'phone_number']


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'invoice', 'name', 'unit', 'amount', 'net_price', 'vat']


class InvoiceSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True)

    class Meta:
        model = Invoice
        fields = ['company', 'invoice_type', 'payment_method', 'create_date', 'sale_date', 'payment_date',
                  'account_number', 'invoice_number', 'invoice_pdf', 'currency', 'items']
















