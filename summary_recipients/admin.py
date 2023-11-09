from django.contrib import admin

from summary_recipients.models import SummaryRecipient


@admin.register(SummaryRecipient)
class SummaryRecipientAdmin(admin.ModelAdmin):
    list_display = (
        "description",
        "day",
        "email",
        "settlement_types",
        "company",
        "final_call",
    )
    list_filter = (
        "day",
        "email",
        "final_call",
    )
    search_fields = ("email", "company__name")
