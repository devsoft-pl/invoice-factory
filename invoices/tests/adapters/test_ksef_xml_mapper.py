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

    def test_map_ksef_xml_to_payment_invalid_xml(self):
        broken_xml = "<h1>To nie jest XML"

        result = map_ksef_xml_to_payment(broken_xml)

        assert result == {"account_number": None, "payment_method": None}

    def test_map_ksef_xml_to_payment_missing_fa_tag(self):
        xml = f"<Faktura {XMLNS}></Faktura>"

        result = map_ksef_xml_to_payment(xml)

        assert result == {"account_number": None, "payment_method": None}

    def test_map_ksef_xml_to_payment_missing_platnosc_tag(self):
        xml = f"""
        <Faktura {XMLNS}>
            <Fa>
                <Dane>Inne dane bez platnosci</Dane>
            </Fa>
        </Faktura>
        """

        result = map_ksef_xml_to_payment(xml)

        assert result == {"account_number": None, "payment_method": None}

    def test_map_ksef_xml_to_payment_with_account_number(self):
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
