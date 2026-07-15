from decimal import Decimal

from invoices.adapters.ksef_xml_mapper import (
    map_ksef_xml_to_items,
    map_ksef_xml_to_payment,
)
from invoices.models import Invoice

XMLNS = 'xmlns="http://crd.gov.pl/wzor/2025/06/25/13775/"'


class TestKSeFXMLMapper:

    def test_map_ksef_xml_to_items_invalid_xml(self):
        broken_xml = "<Faktura><Fa><FaWiersz>Brak domknięcia"

        result = map_ksef_xml_to_items(broken_xml)

        assert result == []

    def test_map_ksef_xml_to_items_missing_fa_tag(self):
        xml_without_fa = f"<Faktura {XMLNS}></Faktura>"

        result = map_ksef_xml_to_items(xml_without_fa)

        assert result == []

    def test_map_ksef_xml_to_items_valid_data(self):
        xml = f"""
        <Faktura {XMLNS}>
            <Fa>
                <FaWiersz>
                    <P_7>Usługa IT</P_7>
                    <P_8B>2.00</P_8B>
                    <P_9A>150.50</P_9A>
                    <P_12>23</P_12>
                </FaWiersz>

                <FaWiersz>
                    <P_7>Konsultacje</P_7>
                </FaWiersz>
            </Fa>
        </Faktura>
        """

        items = map_ksef_xml_to_items(xml)

        assert len(items) == 2
        assert items[0]["name"] == "Usługa IT"
        assert items[0]["amount"] == 2
        assert items[0]["net_price"] == Decimal("150.50")
        assert items[0]["vat_rate"] == 23
        assert items[1]["name"] == "Konsultacje"
        assert items[1]["amount"] == 1
        assert items[1]["net_price"] == Decimal("0")
        assert items[1]["vat_rate"] == 0

    def test_map_ksef_xml_to_items_rounds_fractional_quantity(self):
        xml = f"""
        <Faktura {XMLNS}>
            <Fa>
                <FaWiersz>
                    <P_7>Usługi konsultingowe</P_7>
                    <P_8B>7.5</P_8B>
                    <P_9A>100.00</P_9A>
                    <P_12>23</P_12>
                </FaWiersz>
            </Fa>
        </Faktura>
        """

        items = map_ksef_xml_to_items(xml)

        assert len(items) == 1
        # 7.5 units can't be stored (Item.amount is a whole-number field), so
        # the quantity is rounded but net_price is adjusted to preserve the
        # true line total (7.5 * 100.00 == 750.00).
        assert items[0]["amount"] == 8
        assert items[0]["net_price"] == Decimal("93.75")
        assert items[0]["amount"] * items[0]["net_price"] == Decimal("750.00")

    def test_map_ksef_xml_to_items_never_rounds_quantity_to_zero(self):
        xml = f"""
        <Faktura {XMLNS}>
            <Fa>
                <FaWiersz>
                    <P_7>Drobna usługa</P_7>
                    <P_8B>0.3</P_8B>
                    <P_9A>10.00</P_9A>
                    <P_12>23</P_12>
                </FaWiersz>
            </Fa>
        </Faktura>
        """

        items = map_ksef_xml_to_items(xml)

        assert items[0]["amount"] == 1
        assert items[0]["net_price"] == Decimal("3.00")

    def test_map_ksef_xml_to_payment_invalid_xml(self):
        broken_xml = "<h1>To nie jest XML"

        result = map_ksef_xml_to_payment(broken_xml)

        assert result == {
            "account_number": None,
            "payment_method": None,
            "due_date": None,
        }

    def test_map_ksef_xml_to_payment_missing_fa_tag(self):
        xml = f"<Faktura {XMLNS}></Faktura>"

        result = map_ksef_xml_to_payment(xml)

        assert result == {
            "account_number": None,
            "payment_method": None,
            "due_date": None,
        }

    def test_map_ksef_xml_to_payment_missing_platnosc_tag(self):
        xml = f"""
        <Faktura {XMLNS}>
            <Fa>
                <Dane>Inne dane bez platnosci</Dane>
            </Fa>
        </Faktura>
        """

        result = map_ksef_xml_to_payment(xml)

        assert result == {
            "account_number": None,
            "payment_method": None,
            "due_date": None,
        }

    def test_map_ksef_xml_to_payment_with_account_number(self):
        # Per the official FA(3) schema, the account number is nested under
        # Platnosc/RachunekBankowy/NrRB — not a direct child of Platnosc.
        xml = f"""
        <Faktura {XMLNS}>
            <Fa>
                <Platnosc>
                    <RachunekBankowy>
                        <NrRB>11112222333344445555666677</NrRB>
                    </RachunekBankowy>
                </Platnosc>
            </Fa>
        </Faktura>
        """

        result = map_ksef_xml_to_payment(xml)

        assert result["account_number"] == "11112222333344445555666677"
        assert result["payment_method"] == Invoice.BANK_TRANSFER

    def test_map_ksef_xml_to_payment_without_account_number(self):
        xml = f"""
        <Faktura {XMLNS}>
            <Fa>
                <Platnosc>
                    <Zaplacono>1</Zaplacono>
                </Platnosc>
            </Fa>
        </Faktura>
        """

        result = map_ksef_xml_to_payment(xml)

        assert result["account_number"] is None
        assert result["payment_method"] is None

    def test_map_ksef_xml_to_payment_ignores_direct_nrrachunku(self):
        # A flat NrRachunku directly under Platnosc does not exist in the real
        # FA(3) schema, so it must not be picked up as an account number.
        xml = f"""
        <Faktura {XMLNS}>
            <Fa>
                <Platnosc>
                    <NrRachunku>11112222333344445555666677</NrRachunku>
                </Platnosc>
            </Fa>
        </Faktura>
        """

        result = map_ksef_xml_to_payment(xml)

        assert result["account_number"] is None
        assert result["payment_method"] is None

    def test_map_ksef_xml_to_payment_with_due_date(self):
        xml = f"""
        <Faktura {XMLNS}>
            <Fa>
                <Platnosc>
                    <TerminPlatnosci>
                        <Termin>2026-05-01</Termin>
                    </TerminPlatnosci>
                </Platnosc>
            </Fa>
        </Faktura>
        """

        result = map_ksef_xml_to_payment(xml)

        assert result["due_date"] == "2026-05-01"

    def test_map_ksef_xml_to_payment_without_due_date(self):
        xml = f"""
        <Faktura {XMLNS}>
            <Fa>
                <Platnosc>
                    <Zaplacono>1</Zaplacono>
                </Platnosc>
            </Fa>
        </Faktura>
        """

        result = map_ksef_xml_to_payment(xml)

        assert result["due_date"] is None
