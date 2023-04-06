from django.contrib import admin

from .models import Currency, Invoice, Item, VatRate


class ItemInline(admin.TabularInline):
    model = Item
    extra = 1


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number",
        "company",
        "payment_date",
        "net_amount",
        "gross_amount",
        "currency",
        "user",
    )
    list_filter = (
        "is_recurring",
        "company__name",
        "invoice_type",
        "payment_date",
        "user",
    )
    search_fields = ("invoice_number", "company__name", "user__username")
    inlines = [ItemInline]
    fieldsets = (
        ("User", {"fields": (("user",),)}),
        (
            "Basic information",
            {
                "fields": (
                    ("invoice_number", "invoice_type"),
                    ("company",),
                    ("create_date", "sale_date", "payment_date"),
                )
            },
        ),
        (
            "Advanced options",
            {
                "fields": (
                    ("payment_method", "currency"),
                    ("account_number",),
                )
            },
        ),
        (
            "Recurring invoice",
            {
                "fields": ("recurring_frequency", "is_recurring"),
            },
        ),
    )


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
