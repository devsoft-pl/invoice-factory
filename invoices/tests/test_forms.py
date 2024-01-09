import pytest

from companies.factories import CompanyFactory
from companies.models import Company
from currencies.factories import CurrencyFactory
from currencies.models import Currency
from invoices.factories import (InvoiceBuyDictFactory, InvoiceBuyFactory,
                                InvoiceSellDictFactory, InvoiceSellFactory)
from invoices.forms import (InvoiceBuyForm, InvoiceFilterForm, InvoiceSellForm,
                            InvoiceSellPersonForm)
from invoices.models import Invoice
from persons.factories import PersonFactory
from users.factories import UserFactory


@pytest.mark.django_db
class TestSellInvoiceForm:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.user = UserFactory.create()

        self.currency_1 = CurrencyFactory.create(user=self.user)
        self.currency_2 = CurrencyFactory.create()

        self.company_1 = CompanyFactory.create(
            name="Devsoft", user=self.user, is_my_company=True
        )
        self.company_2 = CompanyFactory.create(name="Microsoft", user=self.user)

        self.client_1 = CompanyFactory.create(
            name="Faktoria", user=self.user, is_my_company=False
        )
        self.client_2 = CompanyFactory.create(name="Santander", user=self.user)

        self.invoice_1 = InvoiceSellFactory.create(
            invoice_number="1/2022", client=self.client_1, company=self.company_1
        )
        self.invoice_2 = InvoiceSellFactory.create(
            invoice_number="4/2022", client=self.client_2, company=self.company_2
        )

    @pytest.mark.parametrize(
        "invoice_number, expected_count", [["1", 1], ["1/2022", 1]]
    )
    def test_returns_filtered_with_different_parts_of_invoice_name(
        self, invoice_number, expected_count
    ):
        request_get = {"invoice_number": invoice_number}

        self.form = InvoiceFilterForm(request_get)
        self.form.is_valid()

        invoices_list = Invoice.objects.filter(company__user=self.user)
        filtered_list = self.form.get_filtered_invoices(invoices_list)

        assert self.invoice_1.id == filtered_list[0].id
        assert filtered_list.count() == expected_count

    def test_returns_filtered_with_common_parts_of_invoice_name(self):
        request_get = {"invoice_number": "2022"}

        self.form = InvoiceFilterForm(request_get)
        self.form.is_valid()

        invoices_list = Invoice.objects.filter(company__user=self.user)
        filtered_list = self.form.get_filtered_invoices(invoices_list)

        assert filtered_list.count() == 2

    def test_return_filtered_empty_list_when_invoice_number_not_exist(self):
        request_get = {"invoice_number": "5/2022"}

        self.form = InvoiceFilterForm(request_get)
        self.form.is_valid()

        invoices_list = Invoice.objects.filter(company__user=self.user)
        filtered_list = self.form.get_filtered_invoices(invoices_list)

        assert filtered_list.count() == 0

    @pytest.mark.parametrize(
        "invoice_type, expected_count",
        [[Invoice.INVOICE_SALES, 2], [Invoice.INVOICE_PURCHASE, 0]],
    )
    def test_returns_list_with_different_invoice_type(
        self, invoice_type, expected_count
    ):
        request_get = {"invoice_type": invoice_type}

        self.form = InvoiceFilterForm(request_get)
        self.form.is_valid()

        invoices_list = Invoice.objects.filter(company__user=self.user)
        filtered_list = self.form.get_filtered_invoices(invoices_list)

        assert filtered_list.count() == expected_count

    @pytest.mark.parametrize(
        "company_name, expected_count", [["Dev", 1], ["Devsoft", 1]]
    )
    def test_return_filtered_company_with_different_name(
        self, company_name, expected_count
    ):
        request_get = {"company": company_name}

        self.form = InvoiceFilterForm(request_get)
        self.form.is_valid()

        invoices_list = Invoice.objects.filter(company__user=self.user)
        filtered_list = self.form.get_filtered_invoices(invoices_list)

        assert self.invoice_1.id == filtered_list[0].id
        assert filtered_list.count() == expected_count

    @pytest.mark.parametrize(
        "client_name, expected_count", [["Fakt", 1], ["Faktoria", 1]]
    )
    def test_return_filtered_client_with_different_name(
        self, client_name, expected_count
    ):
        request_get = {"client": client_name}

        self.form = InvoiceFilterForm(request_get)
        self.form.is_valid()

        invoices_list = Invoice.objects.filter(company__user=self.user)
        filtered_list = self.form.get_filtered_invoices(invoices_list)

        assert self.invoice_1.id == filtered_list[0].id
        assert filtered_list.count() == expected_count

    def test_filtered_currency_current_user(self):
        self.form = InvoiceSellForm(current_user=self.user)
        form_currencies_ids = self.form.fields["currency"].queryset.values_list(
            "id", flat=True
        )

        user_currencies_ids = Currency.objects.filter(user=self.user).values_list(
            "id", flat=True
        )

        assert set(form_currencies_ids) == set(user_currencies_ids)
        assert form_currencies_ids.count() == user_currencies_ids.count()

    def test_filtered_company_current_user(self):
        self.form = InvoiceSellForm(current_user=self.user)
        form_companies_ids = self.form.fields["company"].queryset.values_list(
            "id", flat=True
        )

        user_companies_ids = Company.objects.filter(
            user=self.user, is_my_company=True
        ).values_list("id", flat=True)

        assert set(form_companies_ids) == set(user_companies_ids)
        assert form_companies_ids.count() == user_companies_ids.count()

    def test_filtered_client_current_user(self):
        self.form = InvoiceSellForm(current_user=self.user)
        form_companies_ids = self.form.fields["client"].queryset.values_list(
            "id", flat=True
        )

        user_companies_ids = Company.objects.filter(
            user=self.user, is_my_company=False
        ).values_list("id", flat=True)

        assert set(form_companies_ids) == set(user_companies_ids)
        assert form_companies_ids.count() == user_companies_ids.count()

    @pytest.mark.parametrize(
        "validator, create_correction",
        [
            [
                "Numer faktury należy wprowadzać cyfrowo, wyłącznie w formacie numer/rrrr",
                False,
            ],
            ["Wprowadź numer faktury korygującej tylko w formacie numer/k/rrrr", True],
        ],
    )
    def test_form_with_not_valid_data(self, validator, create_correction):
        data = InvoiceSellDictFactory(
            company=self.company_1,
            client=self.client_1,
        )
        form = InvoiceSellForm(
            data=data, current_user=self.user, create_correction=create_correction
        )
        is_valid = form.is_valid()

        assert form.errors == {
            "invoice_number": [validator],
            "currency": ["To pole jest wymagane."],
            "account_number": [
                "Wpisz numer rachunku bez znaków specjalnych składający się z min. 15 znaków"
            ],
        }
        assert not is_valid

    @pytest.mark.parametrize(
        "invoice_number, create_correction", [["1/2023", False], ["1/k/2023", True]]
    )
    def test_invoice_sell_with_valid_data(self, invoice_number, create_correction):
        data = InvoiceSellDictFactory(
            company=self.company_1,
            client=self.client_1,
            currency=self.currency_1,
            invoice_number=invoice_number,
            account_number="111111111111111",
        )

        form = InvoiceSellForm(
            current_user=self.user, data=data, create_correction=create_correction
        )
        is_valid = form.is_valid()

        assert form.errors == {}
        assert is_valid

    @pytest.mark.parametrize(
        "invoice_number, create_correction", [["1/2023", False], ["1/k/2023", True]]
    )
    def test_invoice_sell_person_with_valid_data(
        self, invoice_number, create_correction
    ):
        person = PersonFactory.create(user=self.user)
        data = InvoiceSellDictFactory(
            company=self.company_1,
            client=person,
            currency=self.currency_1,
            invoice_number=invoice_number,
            account_number="111111111111111",
        )

        form = InvoiceSellPersonForm(
            current_user=self.user, data=data, create_correction=create_correction
        )
        is_valid = form.is_valid()

        assert form.errors == {}
        assert is_valid

    def test_clean_invoice_number_returns_error_for_client(self):
        data = InvoiceSellDictFactory(
            company=self.company_1,
            client=self.client_1,
            currency=self.currency_1,
            invoice_number=self.invoice_1.invoice_number,
        )

        form = InvoiceSellForm(current_user=self.user, data=data)

        assert not form.is_valid()
        assert form.errors == {
            "invoice_number": ["Numer faktury już istnieje"],
            "account_number": [
                "Wpisz numer rachunku bez znaków specjalnych składający się z min. 15 znaków"
            ],
        }

    def test_clean_invoice_number_returns_error_for_person(self):
        person = CompanyFactory.create(user=self.user)
        data = InvoiceSellDictFactory(
            company=self.company_1,
            person=person,
            currency=self.currency_1,
            invoice_number=self.invoice_1.invoice_number,
        )

        form = InvoiceSellPersonForm(current_user=self.user, data=data)

        assert not form.is_valid()
        assert form.errors == {
            "invoice_number": ["Numer faktury już istnieje"],
            "person": [
                "Wybierz poprawną wartość. Podana nie jest jednym z dostępnych wyborów."
            ],
            "account_number": [
                "Wpisz numer rachunku bez znaków specjalnych składający się z min. 15 znaków"
            ],
        }


@pytest.mark.django_db
class TestBuyInvoiceForm:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.user = UserFactory.create()
        self.company = CompanyFactory.create(
            name="Devsoft", user=self.user, is_my_company=True
        )
        self.invoice = InvoiceBuyFactory.create(
            invoice_number="1/2022", company=self.company
        )

    @pytest.mark.parametrize(
        "invoice_type, expected_count",
        [[Invoice.INVOICE_SALES, 0], [Invoice.INVOICE_PURCHASE, 1]],
    )
    def test_returns_list_with_different_invoice_type(
        self, invoice_type, expected_count
    ):
        request_get = {"invoice_type": invoice_type}

        self.form = InvoiceFilterForm(request_get)
        self.form.is_valid()

        invoices_list = Invoice.objects.filter(company__user=self.user)
        filtered_list = self.form.get_filtered_invoices(invoices_list)

        assert filtered_list.count() == expected_count

    def test_form_with_valid_data(self):
        data = InvoiceBuyDictFactory(
            company=self.company,
            invoice_number="1/2023",
        )
        files = {"invoice_file": data["invoice_file"]}

        form = InvoiceBuyForm(current_user=self.user, data=data, files=files)

        assert form.is_valid()
        assert form.errors == {}

    def test_clean_invoice_number_returns_error(self):
        data = InvoiceBuyDictFactory(
            company=self.company,
            invoice_number=self.invoice.invoice_number,
        )
        files = {"invoice_file": data["invoice_file"]}

        form = InvoiceBuyForm(current_user=self.user, data=data, files=files)

        assert not form.is_valid()
        assert form.errors == {
            "invoice_number": ["Numer faktury już istnieje"],
        }
