from rest_framework import viewsets

from accountants.models import Accountant
from accountants.serializers import AccountantSerializer
from base.mixins import OwnedObjectsMixin


class AccountantViewSet(OwnedObjectsMixin, viewsets.ModelViewSet):
    queryset = Accountant.objects.all()
    serializer_class = AccountantSerializer
