from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from companies.models import Company


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
                "fields": ("name", "nip", "regon", "created_at"),
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
        (
            _("KSeF information"),
            {
                "fields": ("ksef_token", "ksef_last_fetched_at"),
            },
        ),
    )
