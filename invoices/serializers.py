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
        fields = '__all__'


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ('id', 'code', 'symbol')
        extra_kwargs = {
            'code': {'validators': []},
            'symbol': {'validators': []},
        }


class CompanySerializer(serializers.ModelSerializer):
    default_currency = CurrencySerializer(many=False)

    class Meta:
        model = Company
        fields = ['name', 'nip', 'address', 'zip_code', 'city', 'email', 'phone_number', 'default_currency']

    def create(self, validated_data):
        default_currency = validated_data.pop('default_currency')
        code = default_currency['code']
        symbol = default_currency['symbol']
        default_currency, created = Currency.objects.get_or_create(code=code, symbol=symbol)
        validated_data['default_currency'] = default_currency

        company = Company.objects.create(**validated_data)
        return company


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'


class InvoiceSerializer(serializers.ModelSerializer):
    company = CompanySerializer(many=False)
    currency = CurrencySerializer(many=False)

    class Meta:
        model = Invoice
        fields = ['company', 'invoice_type', 'payment_method', 'create_date', 'sale_date', 'payment_date',
                  'account_number', 'invoice_number', 'invoice_pdf', 'currency']

    def create(self, validated_data):
        company = validated_data.pop('company')
        name = company['name']
        nip = company['nip']
        address = company['address']
        zip_code = company['zip_code']
        city = company['city']
        email = company['email']
        phone_number = company['phone_number']
        default_currency = company['default_currency']
        company, created = Company.objects.get_or_create(name=name, nip=nip, address=address, zip_code=zip_code,
                                                         city=city, email=email, phone_number=phone_number,
                                                         default_currency=default_currency)
        validated_data['company'] = company

        currency = validated_data.pop('currency')
        code = currency['code']
        symbol = currency['symbol']
        currency, created = Currency.objects.get_or_create(code=code, symbol=symbol)
        validated_data['currency'] = currency

        invoice = Invoice.objects.create(**validated_data)
        return invoice





