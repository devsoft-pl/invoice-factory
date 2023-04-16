from django.contrib.auth.models import User
from rest_framework import viewsets

from users.serializers import UserSerializer


class OwnedObjectsMixin:
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return super().get_queryset()
        else:
            return super().get_queryset().filter(user_id=user.id)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return super().get_queryset()
        else:
            return super().get_queryset().filter(id=user.id)
