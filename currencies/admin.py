from django.contrib import admin

from currencies.models import Currency


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ("code", "user")
    list_filter = ("user",)
    fieldsets = (
        (
            "Basic information",
            {
                "fields": ("code", "user"),
            },
        ),
    )
