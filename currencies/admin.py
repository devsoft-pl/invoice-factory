from django.contrib import admin
from django.utils.translation import gettext as _

from currencies.models import Currency


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ("code", "user")
    list_filter = ("user",)
    fieldsets = (
        (
            _("Basic information"),
            {
                "fields": ("code", "user"),
            },
        ),
    )
