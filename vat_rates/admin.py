from django.contrib import admin

from vat_rates.models import VatRate


@admin.register(VatRate)
class VatRateAdmin(admin.ModelAdmin):
    list_display = ("rate", "user")
    list_filter = ("user",)
    fieldsets = (
        (
            "Basic information",
            {
                "fields": ("rate", "user"),
            },
        ),
    )
