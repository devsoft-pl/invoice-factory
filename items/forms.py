from django import forms

from items.models import Item


class ItemForm(forms.ModelForm):
    next = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Item
        fields = ["next", "invoice", "name", "pkwiu", "amount", "net_price", "vat"]
        labels = {
            "name": "Nazwa",
            "pkwiu": "PKWiU",
            "amount": "Ilość",
            "net_price": "Cena netto",
            "vat": "Vat",
        }
