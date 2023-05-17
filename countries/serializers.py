from rest_framework import serializers

from countries.models import Country


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ("id", "country", "user", "is_my_country")
        extra_kwargs = {
            "code": {"validators": []},
        }
