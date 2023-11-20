from django.contrib import admin

from persons.models import Person


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "address", "zip_code", "city", "country")
    search_fields = ("first_name", "last_name")

    fieldsets = (
        (
            _("Person info"),
            {
                "fields": ("first_name", "last_name"),
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