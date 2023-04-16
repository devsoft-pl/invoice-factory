from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator


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
