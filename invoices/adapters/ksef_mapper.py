from datetime import date
from decimal import Decimal

from invoices.adapters.ksef_xml_mapper import (
    map_ksef_xml_to_items,
    map_ksef_xml_to_payment,
)
from invoices.models import Invoice


def map_ksef_invoice_to_dict(ksef_invoice: dict, company, xml: str = None) -> dict:
    """
    Map a KSeF invoice metadata dict to a field dict ready to create an Invoice instance.
    Does not write to the database. If xml is provided, account_number and payment_method
    are populated from the FA(3) document.
    """
    payment = (
        map_ksef_xml_to_payment(xml)
        if xml
        else {"account_number": None, "payment_method": None}
    )

    return {
        "invoice_number": ksef_invoice.get("invoiceNumber"),
        "invoice_type": Invoice.INVOICE_PURCHASE,
        "company": company,
        "sale_date": _parse_date(ksef_invoice.get("issueDate")),
        "create_date": _parse_date(ksef_invoice.get("acquisitionDate")),
        "payment_date": _parse_date(ksef_invoice.get("issueDate")),
        "settlement_date": _parse_date(ksef_invoice.get("issueDate")),
        "net_amount": Decimal(str(ksef_invoice.get("netAmount") or 0)),
        "gross_amount": Decimal(str(ksef_invoice.get("grossAmount") or 0)),
        "is_recurring": False,
        "is_settled": False,
        "is_paid": False,
        "account_number": payment["account_number"],
        "payment_method": payment["payment_method"],
    }


def map_ksef_invoice_to_items(xml: str) -> list:
    """Return a list of item dicts parsed from the FA(3) XML."""
    return map_ksef_xml_to_items(xml)


def map_ksef_invoice_to_seller_dict(ksef_invoice: dict) -> dict:
    """Return seller data from a KSeF invoice — for optional Company creation."""
    seller = ksef_invoice.get("seller", {})
    return {
        "nip": seller.get("nip"),
        "name": seller.get("name"),
    }


def _parse_date(value: str) -> date:
    if not value:
        return date.today()
    # issueDate format: "2026-04-01", acquisitionDate format: ISO datetime
    return date.fromisoformat(value[:10])
