from django import forms
from django.core.validators import RegexValidator
from django.utils.translation import gettext as _

from countries.models import Country
from persons.models import Person

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

    def __init__(self, country_user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.country_user = country_user
        self.fields["country"].queryset = Country.objects.filter(
            user=country_user
        ).order_by("country")

        for field in self.Meta.fields:
            self.fields[field].widget.attrs["class"] = "form-control"

        self.fields["zip_code"].validators = [zip_code_validator]
        self.fields["city"].validators = [city_validator]
        self.fields["phone_number"].validators = [phone_number_validator]
