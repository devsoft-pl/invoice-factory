from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from countries.models import Country


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_select_related = ("user",)
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
