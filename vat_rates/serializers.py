from rest_framework import serializers

from vat_rates.models import VatRate


class VatRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VatRate
        fields = ("id", "rate", "user", "is_my_vat")
        extra_kwargs = {
            "code": {"validators": []},
        }
