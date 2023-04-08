from django import forms

from items.models import Item


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["name", "pkwiu", "amount", "net_price", "vat"]