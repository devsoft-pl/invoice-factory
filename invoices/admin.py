from django.contrib import admin

from .models import (
    Company,
    Invoice,
    Item,
    VatRate,
    Currency,
)


class ItemInline(admin.TabularInline):
    model = Item
    extra = 1


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'nip', 'email')


class InvoiceAdmin(admin.ModelbAdmin):
    list_display = ('invoice_number', 'company', 'payment_date', 'gross_amount', 'currency')
    list_filter = ('company__name', 'invoice_type')
    search_fields = ('invoice_number', 'company__name')
    inlines = [
        ItemInline
    ]
    fieldsets = (
        ('Dane podstawowe', {
            'fields': (
                ('company', 'invoice_type', 'invoice_number'),
                ('create_date', 'sale_date', 'payment_date'),
            )
        }),
        ('Advanced options', {
            'fields':
                ('payment_method', 'currency'),
        }),
    )


@admin.register(VatRate)
class VatRateAdmin(admin.ModelAdmin):
    pass


admin.site.register(Company, CompanyAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Currency)
