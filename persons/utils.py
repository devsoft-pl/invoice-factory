from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from persons.models import Person


def get_user_person_or_404(person_id, user):
    person = get_object_or_404(Person.objects.select_related("user"), pk=person_id)
    if person.user != user:
        raise Http404(_("Person does not exist"))

    return person
