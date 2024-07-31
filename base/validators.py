from django.core.validators import MaxValueValidator, RegexValidator
from django.utils.translation import gettext_lazy as _

invoice_number_validator = RegexValidator(
    r"^[0-9]+/(0[1-9]|1[0-2])/[0-9]{4}$",
    _(
        "Please enter the invoice number in numeric format only, "
        "following the pattern number/mm/yyyy"
    ),
)

correction_invoice_number_validator = RegexValidator(
    r"^[0-9]+/(0[1-9]|1[0-2])/[0-9]{4}/k$",
    _("Please enter the correction invoice number in the format number/mm/yyyy/c"),
)

nip_validator = RegexValidator(
    r"^[0-9a-zA-Z]{8,16}$",
    _(
        "Please enter the tax ID without special characters "
        "and with a minimum of 8 characters"
    ),
)

pesel_validator = RegexValidator(
    r"^[0-9]{11}$",
    _("Please enter Pesel with 11 numbers"),
)

regon_validator = RegexValidator(
    r"^([0-9]{9,14})$",
    _("Please enter the REGON using minimum 9 numbers"),
)

currency_validator = RegexValidator(
    r"^[a-zA-Z]{3}$", _("Please enter the country code using 3 letters")
)

account_number_validator = RegexValidator(
    r"^[0-9A-Z ]{15,32}$",
    _(
        "Please enter the account number with a minimum of 15 characters, "
        "excluding special characters"
    ),
)

rate_validator = MaxValueValidator(99)

zip_code_validator = RegexValidator(
    r"^[0-9]{2}-[0-9]{3}$",
    _("Please enter the zip code using numbers only in the format xx-xxx"),
)

phone_number_validator = RegexValidator(
    r"^[0-9]{9,}$", _("Please enter a phone using minimum 9 numbers")
)
