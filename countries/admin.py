from django.contrib import admin

from countries.models import Country


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("country", "user")
    list_filter = ("user",)
    fieldsets = (
        (
            "Basic information",
            {
                "fields": ("country", "user"),
            },
        ),
    )
