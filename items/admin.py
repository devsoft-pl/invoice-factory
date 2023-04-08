from django.contrib import admin

from items.models import Item


class ItemInline(admin.TabularInline):
    model = Item
    extra = 1
