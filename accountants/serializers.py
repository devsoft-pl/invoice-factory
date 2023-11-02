from rest_framework import serializers

from accountants.models import Accountant


class AccountantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accountant
        fields = [
            "id",
            "name",
            "email",
            "phone_number",
            "company",
        ]
