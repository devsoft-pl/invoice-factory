import pytest

from companies.factories import CompanyFactory
from currencies.factories import CurrencyFactory
from invoices.factories import InvoiceFactory
from invoices.forms import InvoiceFilterForm
from invoices.models import Invoice
from users.factories import UserFactory


@pytest.mark.django_db
class TestInvoiceForm:
    @pytest.fixture(autouse=True)
    def set_up(self) -> None:
        self.user = UserFactory.create()

        self.currency_1 = CurrencyFactory.create(user=self.user)
        self.currency_2 = CurrencyFactory.create()

        self.company_1 = CompanyFactory.create(name="Devsoft", user=self.user)
        self.company_2 = CompanyFactory.create(name="Microsoft", user=self.user)

        self.client_1 = CompanyFactory.create(name="Faktoria", user=self.user)
        self.client_2 = CompanyFactory.create(name="Santander", user=self.user)

        self.invoice_1 = InvoiceFactory.create(
            invoice_number="1/2022",
            invoice_type=Invoice.INVOICE_SALES,
            client=self.client_1,
            company=self.company_1,
            user=self.user,
        )
        self.invoice_2 = InvoiceFactory.create(
            invoice_number="4/2022",
            invoice_type=Invoice.INVOICE_SALES,
            client=self.client_2,
            company=self.company_2,
            user=self.user,
        )

    def test_return_filtered_invoice_with_invoice_number_startswith(self):
        request_get = {"invoice_number": "1"}
        self.form = InvoiceFilterForm(request_get)
        self.form.is_valid()
        invoices_list = Invoice.objects.filter(user=self.user)
        filtered_list = self.form.get_filtered_invoices(invoices_list)
        assert self.invoice_1.id == filtered_list[0].id
        assert filtered_list.count() == 1

    def test_return_filtered_invoice_with_exact_invoice_number(self):
        request_get = {"invoice_number": "1/2022"}
        self.form = InvoiceFilterForm(request_get)
        self.form.is_valid()
        invoices_list = Invoice.objects.filter(user=self.user)
        filtered_list = self.form.get_filtered_invoices(invoices_list)
        assert self.invoice_1.id == filtered_list[0].id
        assert filtered_list.count() == 1

    def test_returns_filtered_invoices_with_similar_invoice_number(self):
        request_get = {"invoice_number": "2022"}
        self.form = InvoiceFilterForm(request_get)
        self.form.is_valid()
        invoices_list = Invoice.objects.filter(user=self.user)
        filtered_list = self.form.get_filtered_invoices(invoices_list)
        assert filtered_list.count() == 2

    def test_return_filtered_empty_list_when_invoice_invoice_number_not_exist(self):
        request_get = {"invoice_number": "5/2022"}
        self.form = InvoiceFilterForm(request_get)
        self.form.is_valid()
        invoices_list = Invoice.objects.filter(user=self.user)
        filtered_list = self.form.get_filtered_invoices(invoices_list)
        assert filtered_list.count() == 0

    def test_return_list_invoices_with_invoice_sale_type(self):
        request_get = {"invoice_type": Invoice.INVOICE_SALES}
        self.form = InvoiceFilterForm(request_get)
        self.form.is_valid()
        invoices_list = Invoice.objects.filter(user=self.user)
        filtered_list = self.form.get_filtered_invoices(invoices_list)
        assert filtered_list.count() == 2

    def test_return_empty_list_when_invoice_purchase_type_not_exist(self):
        request_get = {"invoice_type": Invoice.INVOICE_PURCHASE}
        self.form = InvoiceFilterForm(request_get)
        self.form.is_valid()
        invoices_list = Invoice.objects.filter(user=self.user)
        filtered_list = self.form.get_filtered_invoices(invoices_list)
        assert filtered_list.count() == 0

    def test_return_filtered_company_with_name_startswith(self):
        request_get = {"company": "Dev"}
        self.form = InvoiceFilterForm(request_get)
        self.form.is_valid()
        invoices_list = Invoice.objects.filter(user=self.user)
        filtered_list = self.form.get_filtered_invoices(invoices_list)
        assert self.invoice_1.id == filtered_list[0].id
        assert filtered_list.count() == 1

    def test_return_filtered_company_with_exact_name(self):
        request_get = {"company": "Devsoft"}
        self.form = InvoiceFilterForm(request_get)
        self.form.is_valid()
        invoices_list = Invoice.objects.filter(user=self.user)
        filtered_list = self.form.get_filtered_invoices(invoices_list)
        assert self.invoice_1.id == filtered_list[0].id
        assert filtered_list.count() == 1

