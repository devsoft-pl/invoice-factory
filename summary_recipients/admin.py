from django.contrib import admin

from summary_recipients.models import SummaryRecipient


@admin.register(SummaryRecipient)
class SummaryRecipientAdmin(admin.ModelAdmin):
    list_display = ("description", "day", "email", "settlement_types", "company")
