from django.contrib import admin

from companies.models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "nip", "email", "phone_number", "user")
    search_fields = ("name", "nip", "regon", "user__username")
    list_filter = ("user",)

    fieldsets = (
        (
            "User info",
            {
                "fields": ("user",),
            },
        ),
        (
            "Basic information",
            {
                "fields": ("name", "nip", "regon"),
            },
        ),
        (
            "Address data",
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
