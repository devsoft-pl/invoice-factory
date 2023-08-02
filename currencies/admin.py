from django.contrib import admin
from django.utils.translation import gettext as _

from currencies.models import Currency, ExchangeRate


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


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ("date", "currency", "buy_rate", "sell_rate")
    list_filter = ("date", "currency__code")
    search_fields = ("currency__code",)
