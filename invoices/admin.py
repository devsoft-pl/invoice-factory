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
    search_fields = ('name', 'nip')

    fieldsets = (
        ('Basic information', {
            'fields':
                ('name', 'nip'),
        }),
        ('Address data', {
            'fields': (
                ('street', 'street_number', 'apartment_number'),
                ('zip_code', 'city'),
            )
        }),
        ('Advanced options', {
            'fields':
                ('email', 'default_currency'),
        }),
    )


class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'company', 'payment_date', 'net_amount', 'gross_amount', 'currency')
    list_filter = ('company__name', 'invoice_type', 'payment_date')
    search_fields = ('invoice_number', 'company__name')
    inlines = [
        ItemInline
    ]
    fieldsets = (
        ('Basic information', {
            'fields': (
                ('invoice_number', 'create_date'),
                ('company', 'invoice_type'),
                ('sale_date', 'payment_date'),
            )
        }),
        ('Advanced options', {
            'fields': (
                ('payment_method', 'currency'),
                ('account_number', ),
            )
        }),
    )


class VatRateAdmin(admin.ModelAdmin):
    list_display = ('rate',)
    fieldsets = (
        ('Basic information', {
            'fields':
                ('rate', ),
        }),
    )


class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'symbol')
    fieldsets = (
        ('Basic information', {
            'fields':
                ('code', 'symbol'),
        }),
    )


admin.site.register(Company, CompanyAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(VatRate, VatRateAdmin)
admin.site.register(Currency, CurrencyAdmin)
