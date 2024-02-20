from django import forms

from items.models import Item
from vat_rates.models import VatRate


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["name", "pkwiu", "amount", "net_price", "vat"]

    def __init__(self, *args, current_user, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_user = current_user
        self.fields["vat"].queryset = VatRate.objects.filter(
            user=current_user
        ).order_by("rate")

        for field in self.Meta.fields:
            self.fields[field].widget.attrs["class"] = "form-control"
