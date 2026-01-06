from django import forms

from items.models import Item
from vat_rates.models import VatRate


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["name", "pkwiu", "amount", "net_price", "vat"]
        widgets = {
            "net_price": forms.TextInput(
                attrs={"type": "text", "class": "form-control"}
            ),
        }

    def __init__(self, *args, current_user, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_user = current_user
        self.fields["vat"].queryset = VatRate.objects.filter(
            user=current_user
        ).order_by("rate")

        for field_name in self.Meta.fields:
            if field_name not in self.Meta.widgets:
                self.fields[field_name].widget.attrs["class"] = "form-control"

        pkwiu_field: forms.CharField = self.fields["pkwiu"]
        pkwiu_field.required = False

        vat_field: forms.ModelChoiceField = self.fields["vat"]
        vat_field.empty_label = "ZW"
