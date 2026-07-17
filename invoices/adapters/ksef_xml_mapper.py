import logging
import xml.etree.ElementTree as ET
from decimal import ROUND_HALF_UP, Decimal

from invoices.models import Invoice

logger = logging.getLogger(__name__)

NS = "http://crd.gov.pl/wzor/2025/06/25/13775/"


def _tag(name):
    return f"{{{NS}}}{name}"


def map_ksef_xml_to_items(xml_string: str) -> list:
    """
    Parse FA(3) XML and return a list of dicts ready to create Item instances.
    Keys: name, amount, net_price, vat_rate (percentage as int).
    """
    try:
        root = ET.fromstring(xml_string)
    except ET.ParseError as e:
        logger.error("KSeF XML parsing failed: %s", e)
        return []

    fa = root.find(_tag("Fa"))
    if fa is None:
        return []

    items = []
    for row in fa.findall(_tag("FaWiersz")):
        name = _text(row, "P_7") or ""
        raw_amount = Decimal(_text(row, "P_8B") or "1")
        raw_net_price = Decimal(_text(row, "P_9A") or "0")
        vat_rate = int(_text(row, "P_12") or "0")

        amount = int(raw_amount.to_integral_value(rounding=ROUND_HALF_UP)) or 1

        if amount == raw_amount:
            net_price = raw_net_price
        else:
            # Item.amount only stores whole units. Fold the fractional quantity
            # into net_price so amount * net_price still matches the invoice's
            # true line total, instead of silently discarding the fraction.
            line_net_total = raw_amount * raw_net_price
            net_price = (line_net_total / amount).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            logger.warning(
                "KSeF item '%s' has fractional quantity %s; rounded to %d and "
                "adjusted net_price from %s to %s to preserve the line total",
                name,
                raw_amount,
                amount,
                raw_net_price,
                net_price,
            )

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
    Parse FA(3) XML and return a dict with payment data.
    Keys: account_number (str|None), payment_method (int|None), due_date (str|None).
    """
    empty_result = {"account_number": None, "payment_method": None, "due_date": None}

    try:
        root = ET.fromstring(xml_string)
    except ET.ParseError as e:
        logger.error("KSeF XML parsing failed: %s", e)
        return empty_result

    fa = root.find(_tag("Fa"))
    if fa is None:
        return empty_result

    payment_node = fa.find(_tag("Platnosc"))
    if payment_node is None:
        return empty_result

    # Platnosc/RachunekBankowy/NrRB — bank account number (element is nested
    # under RachunekBankowy per the FA(3) schema; may be absent, and multiple
    # accounts may be listed — we take the first one)
    bank_account_node = payment_node.find(_tag("RachunekBankowy"))
    account_number = (
        _text(bank_account_node, "NrRB") if bank_account_node is not None else None
    )

    # map to BANK_TRANSFER if account number is present, otherwise None
    if account_number:
        payment_method = Invoice.BANK_TRANSFER
    else:
        payment_method = None

    # Platnosc/TerminPlatnosci/Termin — payment due date (may be absent, or
    # repeated for installment payments — we take the first one)
    payment_term_node = payment_node.find(_tag("TerminPlatnosci"))
    due_date = (
        _text(payment_term_node, "Termin") if payment_term_node is not None else None
    )

    return {
        "account_number": account_number,
        "payment_method": payment_method,
        "due_date": due_date,
    }


def _text(element, tag) -> str | None:
    child = element.find(_tag(tag))
    return child.text if child is not None else None
