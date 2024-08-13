from django import forms
from django.utils.translation import gettext_lazy as _

from base.validators import (
    nip_validator,
    pesel_validator,
    phone_number_validator,
    zip_code_validator,
)
from countries.models import Country
from persons.models import Person


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = [
            "first_name",
            "last_name",
            "nip",
            "pesel",
            "address",
            "zip_code",
            "city",
            "country",
            "email",
            "phone_number",
        ]

    def __init__(self, current_user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_user = current_user
        self.fields["country"].queryset = Country.objects.filter(
            user=current_user
        ).order_by("country")

        for field in self.Meta.fields:
            self.fields[field].widget.attrs["class"] = "form-control"

        self.fields["zip_code"].validators = [zip_code_validator]
        self.fields["phone_number"].validators = [phone_number_validator]
        self.fields["nip"].validators = [nip_validator]
        self.fields["pesel"].validators = [pesel_validator]

    def clean_nip(self):
        nip = self.cleaned_data.get("nip")
        if not nip:
            return nip

        person = Person.objects.filter(nip=nip, user=self.current_user)

        if self.instance.pk:
            person = person.exclude(pk=self.instance.pk)

        if person.exists():
            raise forms.ValidationError(_("Nip already exists"))

        return nip

    def clean_pesel(self):
        pesel = self.cleaned_data.get("pesel")
        if not pesel:
            return pesel

        person = Person.objects.filter(pesel=pesel, user=self.current_user)

        if self.instance.pk:
            person = person.exclude(pk=self.instance.pk)

        if person.exists():
            raise forms.ValidationError(_("Pesel already exists"))

        return pesel

    def clean(self):
        first_name = self.cleaned_data.get("first_name")
        last_name = self.cleaned_data.get("last_name")
        address = self.cleaned_data.get("address")
        zip_code = self.cleaned_data.get("zip_code")
        city = self.cleaned_data.get("city")
        person = Person.objects.filter(
            first_name=first_name,
            last_name=last_name,
            address=address,
            city=city,
            zip_code=zip_code,
            user=self.current_user,
        )

        if self.instance.pk:
            person = person.exclude(pk=self.instance.pk)

        if person.exists():
            raise forms.ValidationError(_("Person with given data already exists"))

        return self.cleaned_data


class PersonFilterForm(forms.Form):
    first_name = forms.CharField(label=_("First name"), required=False)
    last_name = forms.CharField(label=_("Last name"), required=False)
    address = forms.CharField(label=_("Address"), required=False)

    first_name.widget.attrs.update({"class": "form-control"})
    last_name.widget.attrs.update({"class": "form-control"})
    address.widget.attrs.update({"class": "form-control"})

    def get_filtered_persons(self, persons_list):
        first_name = self.cleaned_data["first_name"]
        last_name = self.cleaned_data["last_name"]
        address = self.cleaned_data["address"]

        if first_name:
            persons_list = persons_list.filter(first_name__icontains=first_name)
        if last_name:
            persons_list = persons_list.filter(last_name__icontains=last_name)
        if address:
            persons_list = persons_list.filter(address__icontains=address)

        return persons_list
