from django.contrib import admin
from django.utils.translation import gettext as _

from companies.models import Company, SummaryRecipient


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "nip", "email", "phone_number", "user")
    search_fields = ("name", "nip", "regon", "user__username")
    list_filter = ("user",)

    fieldsets = (
        (
            _("User info"),
            {
                "fields": ("user",),
            },
        ),
        (
            _("Basic information"),
            {
                "fields": ("name", "nip", "regon"),
            },
        ),
        (
            _("Address data"),
            {
                "fields": (
                    ("address",),
                    ("zip_code", "city"),
                    ("country",),
                    ("email", "phone_number"),
                )
            },
        ),
    )


@admin.register(SummaryRecipient)
class SummaryRecipientAdmin(admin.ModelAdmin):
    list_display = ("description", "company", "day", "email", "settlement_types")