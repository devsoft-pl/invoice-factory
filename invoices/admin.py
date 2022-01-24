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


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'nip', 'email', 'phone_number')
    search_fields = ('name', 'nip')

    fieldsets = (
        ('Basic information', {
            'fields':
                ('name', 'nip'),
        }),
        ('Address data', {
            'fields': (
                ('address', ),
                ('zip_code', 'city'),
                ('phone_number', )
            )
        }),
        ('Advanced options', {
            'fields':
                ('email', ),
        }),
    )


@admin.register(Invoice)
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
                ('invoice_number', 'create_date', 'invoice_pdf'),
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


@admin.register(VatRate)
class VatRateAdmin(admin.ModelAdmin):
    list_display = ('rate', 'user')
    list_filter = ('user', )
    fieldsets = (
        ('Basic information', {
            'fields':
                ('rate', 'user'),
        }),
    )


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', )
    fieldsets = (
        ('Basic information', {
            'fields':
                ('code', ),
        }),
    )



