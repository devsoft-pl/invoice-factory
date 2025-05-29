import datetime
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from companies.factories import CompanyFactory
from currencies.factories import CurrencyFactory
from invoices.factories import InvoiceSellFactory
from invoices.models import Invoice, Year
from items.factories import ItemFactory
from reports.forms import ReportFilterForm
from reports.views import get_sum_invoices_per_month
from users.factories import UserFactory


class TestReport(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.set_password("test")
        self.user.save()
        self.currency = CurrencyFactory.create(code="PLN", user=self.user)
        self.company = CompanyFactory.create(user=self.user, is_my_company=True)
        self.invoice: Invoice = InvoiceSellFactory.create(
            currency=self.currency,
            company=self.company,
            sale_date=datetime.date(2023, 1, 31),
            is_recurring=False,
        )
        self.item = ItemFactory.create(invoice=self.invoice)
        self.year = Year.objects.get(year=2023)


class TestListReports(TestReport):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("reports:list_reports")

    def test_list_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_list_if_logged_for_all_revenue(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["invoices"]), 12)
        self.assertEqual(len(response.context["invoices"][0]), 2)
        self.assertTemplateUsed(response, "reports/list_reports.html")

    def test_list_if_logged_for_net(self):
        self.client.login(username=self.user.email, password="test")

        data = {"revenue_type": ReportFilterForm.NETTO, "year": self.year.pk}
        response = self.client.get(self.url, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["net_invoices"]), 12)

        self.assertEqual(
            response.context["net_invoices"][0]["sum"], self.invoice.net_amount
        )
        self.assertTemplateUsed(response, "reports/list_reports.html")

    def test_list_if_logged_for_gross(self):
        self.client.login(username=self.user.email, password="test")

        data = {"revenue_type": ReportFilterForm.GROSS, "year": self.year.pk}
        response = self.client.get(self.url, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["gross_invoices"]), 12)

        invoice_gross_amount_expected = self.invoice.gross_amount.quantize(
            Decimal("0.01")
        )
        invoice_gross_amount = response.context["gross_invoices"][0]["sum"].quantize(
            Decimal("0.01")
        )
        self.assertEqual(invoice_gross_amount, invoice_gross_amount_expected)
        self.assertTemplateUsed(response, "reports/list_reports.html")

    def test_returns_sum_net_invoices_per_month(self):
        invoices = (
            Invoice.objects.filter(company__user=self.user)
            .sales()
            .with_months()
            .with_sum("net_amount")
        )

        invoices = get_sum_invoices_per_month(invoices)

        self.assertEqual(invoices[0], {"month": 1, "sum": self.invoice.net_amount})
        self.assertEqual(invoices[1], {"month": 2, "sum": 0})
        self.assertEqual(len(invoices), 12)

    def test_returns_sum_gross_invoices_per_month(self):
        invoices = (
            Invoice.objects.filter(company__user=self.user)
            .sales()
            .with_months()
            .with_sum("gross_amount")
        )

        invoices = get_sum_invoices_per_month(invoices)
        expected_sum = self.invoice.gross_amount.quantize(Decimal("0.01"))
        invoice_sum = invoices[0]["sum"].quantize(Decimal("0.01"))
        month = invoices[0]["month"]

        self.assertEqual(
            {"month": month, "sum": invoice_sum},
            {"month": 1, "sum": expected_sum},
        )
        self.assertEqual(invoices[1], {"month": 2, "sum": 0})
        self.assertEqual(len(invoices), 12)
