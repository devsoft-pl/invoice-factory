from django.contrib import admin
from django.utils.translation import gettext as _

from countries.models import Country


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("country", "user")
    list_filter = ("user",)
    fieldsets = (
        (
            _("Basic information"),
            {
                "fields": ("country", "user"),
            },
        ),
    )
