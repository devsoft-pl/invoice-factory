from rest_framework import serializers

from persons.models import Person


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = [
            "id",
            "first_name",
            "last_name",
            "address",
            "zip_code",
            "city",
            "country",
            "email",
            "phone_number",
        ]
