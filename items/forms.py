from django import forms

from invoices.models import Invoice
from items.models import Item
from vat_rates.models import VatRate


class ItemForm(forms.ModelForm):
    next = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Item
        fields = ["next", "name", "pkwiu", "amount", "net_price", "vat"]

    def __init__(self, *args, current_user, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["vat"].queryset = VatRate.objects.filter(
            user=current_user
        ).order_by("rate")
        self.fields["name"].widget.attrs["class"] = "form-control"
        self.fields["pkwiu"].widget.attrs["class"] = "form-control"
        self.fields["amount"].widget.attrs["class"] = "form-control"
        self.fields["net_price"].widget.attrs["class"] = "form-control"
        self.fields["vat"].widget.attrs["class"] = "form-control"
