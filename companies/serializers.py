from rest_framework import serializers

from companies.models import Company


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "nip",
            "regon",
            "country",
            "address",
            "zip_code",
            "city",
            "email",
            "phone_number",
            "user",
            "is_my_company"
        ]
