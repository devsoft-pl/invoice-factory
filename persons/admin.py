from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from persons.models import Person


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "address", "zip_code", "city", "user")
    search_fields = ("first_name", "last_name")

    fieldsets = (
        (
            _("Person info"),
            {
                "fields": ("first_name", "last_name", "user"),
            },
        ),
        (
            _("Basic information"),
            {
                "fields": ("address", "zip_code", "city", "country"),
            },
        ),
        (
            _("Additional information"),
            {
                "fields": ("email", "phone_number"),
            },
        ),
    )
