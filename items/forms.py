from django import forms

from items.models import Item


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["invoice", "name", "pkwiu", "amount", "net_price", "vat"]
        labels = {
            "name": "Nazwa",
            "pkwiu": "PKWiU",
            "amount": "Ilość",
            "net_price": "Cena netto",
            "vat": "Vat",
        }
