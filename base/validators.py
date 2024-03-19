from django.core.validators import MaxValueValidator, RegexValidator
from django.utils.translation import gettext as _

invoice_number_validator = RegexValidator(
    r"^[0-9]+/(0[1-9]|1[0-2])/[0-9]{4}$",
    _("Enter invoice number in numbers only in format number/mm/yyyy"),
)

correction_invoice_number_validator = RegexValidator(
    r"^[0-9]+/(0[1-9]|1[0-2])/[0-9]{4}/korekta$",
    _("Enter correction invoice number in only in format number/mm/yyyy/correction"),
)

nip_validator = RegexValidator(
    r"^[0-9a-zA-Z]{8,16}$",
    _("Enter the tax ID without special characters with minimum 8 character"),
)

regon_validator = RegexValidator(
    r"^([0-9]{9}|[0-9]{14})$",
    _("Enter regon in numbers only with minimum 9 character"),
)

currency_validator = RegexValidator(
    r"^[a-zA-Z]{3}$", _("Enter country three letter code")
)

account_number_validator = RegexValidator(
    r"^[0-9A-Z ]{15,32}$",
    _("Enter account number with minimum 15 character without special characters"),
)

rate_validator = MaxValueValidator(99)

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


country_validator = RegexValidator(
    r"^[a-zA-Z ]{2,}$", _("Enter the country in letters only")
)

phone_number_validator = RegexValidator(
    r"^[0-9]{9,}$", _("Enter phone number with 9 numbers only")
)
