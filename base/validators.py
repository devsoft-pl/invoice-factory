import re

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, RegexValidator
from django.utils.translation import gettext_lazy as _

invoice_number_validator = RegexValidator(
    r"^[0-9]+/(0[1-9]|1[0-2])/[0-9]{4}$",
    _("Please  enter the invoice number in the format number/mm/yyyy"),
)

correction_invoice_number_validator = RegexValidator(
    r"^[0-9]+/(0[1-9]|1[0-2])/[0-9]{4}/k$",
    _("Please enter the correction invoice number in the format number/mm/yyyy/c"),
)

pesel_validator = RegexValidator(
    r"^[0-9]{11}$",
    _("Please enter Pesel with 11 numbers"),
)

regon_validator = RegexValidator(
    r"^([0-9]{9,14})$",
    _("Please enter the REGON with a minimum 9 numbers"),
)

currency_validator = RegexValidator(
    r"^[a-zA-Z]{3}$", _("Please enter the code with 3 letters")
)

account_number_validator = RegexValidator(
    r"^[0-9A-Z ]{15,32}$",
    _(
        "Please enter the account number with a minimum of 15 characters and no special characters"
    ),
)

rate_validator = MaxValueValidator(99)

phone_number_validator = RegexValidator(
    r"^[0-9]{9,}$", _("Please enter a phone with a minimum 9 numbers")
)

max_day_validator = MaxValueValidator(31)

polish_nip_validator = RegexValidator(
    r"^\d{10}$",
    _("Polish NIP must consist of 10 digits."),
)

polish_zip_code_validator = RegexValidator(
    r"^\d{2}-\d{3}$",
    _("Polish ZIP code must be in the format XX-XXX."),
)

foreign_zip_code_validator = RegexValidator(
    r"^[A-Za-z0-9\-\s]{2,15}$",
    _("Foreign ZIP code contains invalid characters or is incorrect length."),
)


class ForeignNipValidator:
    def __call__(self, value):
        clean = value.replace(" ", "").replace("-", "")
        if not re.match(r"^[A-Za-z0-9]{4,20}$", clean):
            raise ValidationError(
                _(
                    "Foreign NIP number contains invalid characters or is incorrect length."
                )
            )


foreign_nip_validator = ForeignNipValidator()
