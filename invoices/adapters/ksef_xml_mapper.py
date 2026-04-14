import xml.etree.ElementTree as ET
from decimal import Decimal

from invoices.models import Invoice

NS = "http://crd.gov.pl/wzor/2025/06/25/13775/"


def _tag(name):
    return f"{{{NS}}}{name}"


def map_ksef_xml_to_items(xml_string: str) -> list:
    """
    Parsuje XML FA(3) i zwraca listę słowników gotowych do utworzenia Item.
    Pola: name, amount, net_price, vat_rate (procent jako int)
    """
    root = ET.fromstring(xml_string)
    fa = root.find(_tag("Fa"))
    if fa is None:
        return []

    items = []
    for wiersz in fa.findall(_tag("FaWiersz")):
        name = _text(wiersz, "P_7") or ""
        amount = int(Decimal(_text(wiersz, "P_8B") or "1"))
        net_price = Decimal(_text(wiersz, "P_9A") or "0")
        vat_rate = int(_text(wiersz, "P_12") or "0")

        items.append(
            {
                "name": name,
                "amount": amount,
                "net_price": net_price,
                "vat_rate": vat_rate,
            }
        )

    return items


def map_ksef_xml_to_payment(xml_string: str) -> dict:
    """
    Parsuje XML FA(3) i zwraca słownik z danymi płatności.
    Pola: account_number (str|None), payment_method (int|None)
    """
    root = ET.fromstring(xml_string)
    fa = root.find(_tag("Fa"))
    if fa is None:
        return {"account_number": None, "payment_method": None}

    platnosc = fa.find(_tag("Platnosc"))
    if platnosc is None:
        return {"account_number": None, "payment_method": None}

    # NrRachunku — bank account number (may be absent)
    account_number = _text(platnosc, "NrRachunku")

    # map to BANK_TRANSFER if account number is present, otherwise None
    if account_number:
        payment_method = Invoice.BANK_TRANSFER
    else:
        payment_method = None

    return {
        "account_number": account_number,
        "payment_method": payment_method,
    }


def _text(element, tag) -> str | None:
    child = element.find(_tag(tag))
    return child.text if child is not None else None
