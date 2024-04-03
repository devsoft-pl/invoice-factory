from django.core.validators import MaxValueValidator, RegexValidator
from django.utils.translation import gettext as _

invoice_number_validator = RegexValidator(
    r"^[0-9]+/(0[1-9]|1[0-2])/[0-9]{4}$",
    _("Please enter the invoice number in numeric format only, following the pattern number/mm/yyyy"),
)

correction_invoice_number_validator = RegexValidator(
    r"^[0-9]+/(0[1-9]|1[0-2])/[0-9]{4}/k$",
    _("Please enter the correction invoice number in the format number/mm/yyyy/c"),
)

nip_validator = RegexValidator(
    r"^[0-9a-zA-Z]{8,16}$",
    _("Please enter the tax ID without special characters and with a minimum of 8 characters"),
)

regon_validator = RegexValidator(
    r"^([0-9]{9}|[0-9]{14})$",
    _("Please enter the REGON using numbers only, with a minimum of 9 characters"),
)

currency_validator = RegexValidator(
    r"^[a-zA-Z]{3}$", _("Please enter the country code using three letters")
)

account_number_validator = RegexValidator(
    r"^[0-9A-Z ]{15,32}$",
    _("Please enter the account number with a minimum of 15 characters, excluding special characters"),
)

rate_validator = MaxValueValidator(99)

first_name_validator = RegexValidator(
    r"^[a-zA-Z ]+$", _("Enter the first_name in letters only")
)

last_name_validator = RegexValidator(
    r"^[a-zA-Z ]+$", _("Please enter the last name using letters only")
)

zip_code_validator = RegexValidator(
    r"^[0-9]{2}-[0-9]{3}$", _("Please enter the zip code using numbers only in the format xx-xxx")
)

city_validator = RegexValidator(r"^[a-zA-Z ]+$", _("Please enter the city using letters only"))


country_validator = RegexValidator(
    r"^[a-zA-Z ]{2,}$", _("Please enter the country using letters only")
)

phone_number_validator = RegexValidator(
    r"^[0-9]{9,}$", _("Please enter a phone number with 9 digits only")
)
