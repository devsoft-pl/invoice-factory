from django import forms
from django.core.validators import RegexValidator
from django.utils.translation import gettext as _

from countries.models import Country
from persons.models import Person

first_name_validator = RegexValidator(
    r"^[a-zA-Z ]+$", _("Enter the first_name in letters only")
)

last_name_validator = RegexValidator(
    r"^[a-zA-Z ]+$", _("Enter the last_name in letters only")
)

zip_code_validator = RegexValidator(
    r"^[0-9]{2}-[0-9]{3}$", _("Zip code in numbers only in format xx-xxx")
)

city_validator = RegexValidator(r"^[a-zA-Z ]+$", _("Enter the city in letters only"))

phone_number_validator = RegexValidator(
    r"^[0-9]{9,}$", _("Enter phone number with 9 numbers only")
)


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = [
            "first_name",
            "last_name",
            "address",
            "zip_code",
            "city",
            "country",
            "email",
            "phone_number",
        ]

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields["country"].queryset = Country.objects.filter(
            user=user
        ).order_by("country")

        for field in self.Meta.fields:
            self.fields[field].widget.attrs["class"] = "form-control"

        self.fields["first_name"].validators = [first_name_validator]
        self.fields["last_name"].validators = [last_name_validator]
        self.fields["zip_code"].validators = [zip_code_validator]
        self.fields["city"].validators = [city_validator]
        self.fields["phone_number"].validators = [phone_number_validator]


class PersonFilterForm(forms.Form):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    address = forms.CharField(required=False)

    first_name.widget.attrs.update({"class": "form-control"})
    last_name.widget.attrs.update({"class": "form-control"})
    address.widget.attrs.update({"class": "form-control"})

    def get_filtered_persons(self, persons_list):
        first_name = self.cleaned_data["first_name"]
        last_name = self.cleaned_data["last_name"]
        address = self.cleaned_data["address"]

        if first_name:
            persons_list = persons_list.filter(first_name__contains=first_name)
        if last_name:
            persons_list = persons_list.filter(last_name__contains=last_name)
        if address:
            persons_list = persons_list.filter(address__contains=address)

        return persons_list
