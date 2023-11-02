from django.contrib import admin
from django.utils.translation import gettext as _

from accountants.models import Accountant


@admin.register(Accountant)
class AccountantAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone_number", "company")
    list_filter = ("name", "email")
    fieldsets = (
        (
            _("Basic information"),
            {
                "fields": ("name", "email", "phone_number", "company"),
            },
        ),
    )
