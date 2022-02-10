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
    list_display = ('name', 'nip', 'email', 'phone_number', 'user')
    search_fields = ('name', 'nip', 'user__username')
    list_filter = ('user', )

    fieldsets = (
        ('User info', {
            'fields':
                ('user',),
        }),
        ('Basic information', {
            'fields':
                ('name', 'nip'),
        }),
        ('Address data', {
            'fields': (
                ('address', ),
                ('zip_code', 'city'),
                ('email', 'phone_number')
            )
        }),
    )


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'company', 'payment_date', 'net_amount', 'gross_amount', 'currency', 'user')
    list_filter = ('is_recurring', 'company__name', 'invoice_type', 'payment_date', 'user')
    search_fields = ('invoice_number', 'company__name', 'user__username')
    inlines = [
        ItemInline
    ]
    fieldsets = (
        ('User', {
            'fields': (
                ('user', ),
            )
        }),
        ('Basic information', {
            'fields': (
                ('invoice_number', 'invoice_type'),
                ('company', ),
                ('create_date', 'sale_date', 'payment_date'),
            )
        }),
        ('Advanced options', {
            'fields': (
                ('payment_method', 'currency'),
                ('account_number', ),
            )
        }),
        ('Recurring invoice', {
            'fields':
                ('recurring_frequency', 'is_recurring'),
        }),
        ('Invoice pattern', {
            'fields':
                ('invoice_pdf', )
        })
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
    list_display = ('code', 'user')
    list_filter = ('user',)
    fieldsets = (
        ('Basic information', {
            'fields':
                ('code', 'user'),
        }),
    )



