from django.contrib import admin
from django.utils.translation import gettext as _

from items.admin import ItemInline

from .models import Invoice


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number",
        "company",
        "payment_date",
        "net_amount",
        "gross_amount",
        "currency",
        "is_settled",
    )
    list_filter = (
        "is_recurring",
        "is_settled",
        "company__name",
        "invoice_type",
        "payment_date",
    )
    search_fields = ("invoice_number", "company__name")
    inlines = [ItemInline]
    fieldsets = (
        (
            _("Basic information"),
            {
                "fields": (
                    ("invoice_number", "invoice_type"),
                    ("company",),
                    ("create_date", "sale_date", "payment_date"),
                )
            },
        ),
        (
            _("Advanced options"),
            {
                "fields": (
                    ("payment_method", "currency"),
                    ("account_number",),
                )
            },
        ),
        (
            _("Additional options"),
            {
                "fields": (
                    ("is_recurring",),
                    ("settlement_date", "is_settled"),
                    ("invoice_file",),
                )
            },
        ),
    )
