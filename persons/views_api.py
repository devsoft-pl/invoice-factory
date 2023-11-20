from rest_framework import viewsets

from base.mixins import OwnedObjectsMixin
from persons.models import Person
from persons.serializers import PersonSerializer


class PersonViewSet(OwnedObjectsMixin, viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
