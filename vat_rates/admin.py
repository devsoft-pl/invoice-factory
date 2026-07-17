from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from vat_rates.models import VatRate


@admin.register(VatRate)
class VatRateAdmin(admin.ModelAdmin):
    list_select_related = ("user",)
    list_display = ("rate", "user")
    list_filter = ("user",)
    fieldsets = (
        (
            _("Basic information"),
            {
                "fields": ("rate", "user"),
            },
        ),
    )
