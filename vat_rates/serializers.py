from rest_framework import serializers

from vat_rates.models import VatRate


class VatRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VatRate
        fields = ("id", "rate", "user")
        extra_kwargs = {
            "code": {"validators": []},
        }