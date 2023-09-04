from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.urls import reverse
from parameterized import parameterized

from companies.factories import CompanyFactory
from currencies.factories import CurrencyFactory
from invoices.factories import InvoiceFactory
from invoices.models import Invoice
from users.factories import UserFactory


class TestInvoice(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.set_password("test")
        self.user.save()
        self.user_invoices = sorted(
            InvoiceFactory.create_batch(12, user=self.user),
            key=lambda invoice: invoice.sale_date,
            reverse=True,
        )
        self.other_invoice = InvoiceFactory()


class TestListInvoices(TestInvoice):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("invoices:list_invoices")

    def test_list_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_list_if_logged(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(self.url)
        object_list = response.context["invoices"]

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "invoices/list_invoices.html")
        self.assertTrue(len(object_list) == 10)
        self.assertListEqual(list(object_list), self.user_invoices[:10])

    def test_returns_first_page_when_abc(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(f"{self.url}?page=abc")

        object_list = response.context["invoices"]

        self.assertListEqual(list(object_list), self.user_invoices[:10])

    @parameterized.expand([[2], [666]])
    def test_pagination_return_correct_list(self, page):
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(f"{self.url}?page={page}")
        object_list = response.context["invoices"]

        self.assertTrue(len(object_list) == 2)
        self.assertListEqual(list(object_list), self.user_invoices[10:])


class TestDetailInvoice(TestInvoice):
    def setUp(self) -> None:
        super().setUp()
        self.invoice = self.user_invoices[0]
        self.url = reverse("invoices:detail_invoice", args=[self.invoice.pk])

    def test_detail_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_detail_if_logged(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "invoices/detail_invoice.html")
        self.assertEqual(self.invoice.pk, response.context["invoice"].pk)

    def test_return_404_if_not_my_invoice(self):
        url = reverse("invoices:detail_invoice", args=[self.other_invoice.pk])
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)


class TestDeleteInvoice(TestInvoice):
    def setUp(self) -> None:
        super().setUp()
        self.invoice = self.user_invoices[0]
        self.url = reverse("invoices:delete_invoice", args=[self.invoice.pk])

    def test_delete_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_delete_if_logged(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(self.url)

        with self.assertRaises(ObjectDoesNotExist):
            Invoice.objects.get(pk=self.invoice.pk)
        self.assertEqual(response.status_code, 302)

    def test_return_404_if_not_my_invoice(self):
        url = reverse("invoices:delete_invoice", args=[self.other_invoice.pk])
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)


class TestCreateInvoice(TestInvoice):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("invoices:create_invoice")
        self.company = CompanyFactory.create(user=self.user, is_my_company=True)
        self.contractor = CompanyFactory.create(user=self.user, is_my_company=False)
        self.currency = CurrencyFactory.create(user=self.user)

    def test_create_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_invalid_form_display_errors(self):
        self.client.login(username=self.user.username, password="test")

        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "invoice_number", "To pole jest wymagane."
        )
        self.assertFormError(
            response.context["form"], "create_date", "To pole jest wymagane."
        )
        self.assertTemplateUsed(response, "invoices/create_invoice.html")

    def test_create_with_valid_data(self):
        self.invoice_data = {
            "invoice_number": "1/2023",
            "invoice_type": "0",
            "company": self.company.pk,
            "create_date": "2023-01-01",
            "sale_date": "2023-01-01",
            "payment_date": "2023-01-07",
            "payment_method": "0",
            "currency": self.currency.pk,
            "account_number": "111111111111111",
            "client": self.contractor.pk,
        }
        self.client.login(username=self.user.username, password="test")
        invoices_before_create = Invoice.objects.filter(
            invoice_number="1/2023",
            create_date="2023-01-01",
            currency=self.currency.pk,
            user=self.user,
        ).count()

        response = self.client.post(self.url, self.invoice_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("invoices:list_invoices"))
        self.assertTrue(
            Invoice.objects.filter(
                invoice_number="1/2023",
                create_date="2023-01-01",
                currency=self.currency.pk,
                user=self.user,
            ).exists()
        )
        self.assertEqual(
            Invoice.objects.filter(
                invoice_number="1/2023",
                create_date="2023-01-01",
                currency=self.currency.pk,
                user=self.user,
            ).count(),
            invoices_before_create + 1,
        )

    def test_get_form(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)


class TestReplaceInvoice(TestInvoice):
    def setUp(self) -> None:
        super().setUp()
        self.invoice = self.user_invoices[0]
        self.url = reverse("invoices:replace_invoice", args=[self.invoice.pk])
        self.company = CompanyFactory.create(user=self.user, is_my_company=True)
        self.contractor = CompanyFactory.create(user=self.user, is_my_company=False)
        self.currency = CurrencyFactory.create(user=self.user)

    def test_replace_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_return_404_if_not_my_invoice(self):
        url = reverse("invoices:replace_invoice", args=[self.other_invoice.pk])
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_invalid_form_display_errors(self):
        self.client.login(username=self.user.username, password="test")

        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "sale_date", "To pole jest wymagane."
        )
        self.assertFormError(
            response.context["form"], "create_date", "To pole jest wymagane."
        )
        self.assertTemplateUsed(response, "invoices/replace_invoice.html")

    def test_replace_with_valid_data(self):
        self.invoice_data = {
            "invoice_number": "2/2023",
            "invoice_type": "0",
            "company": self.company.pk,
            "create_date": "2023-02-01",
            "sale_date": "2023-02-01",
            "payment_date": "2023-02-07",
            "payment_method": "0",
            "currency": self.currency.pk,
            "account_number": "111111111111111",
            "client": self.contractor.pk,
        }
        self.client.login(username=self.user.username, password="test")

        response = self.client.post(self.url, self.invoice_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse("invoices:detail_invoice", args=[self.invoice.pk])
        )
        self.assertTrue(
            Invoice.objects.filter(
                invoice_number="2/2023",
                create_date="2023-02-01",
                currency=self.currency.pk,
                user=self.user,
            ).exists()
        )

    def test_get_form(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)


class TestPdfInvoice(TestInvoice):
    def setUp(self) -> None:
        super().setUp()
        self.invoice = self.user_invoices[0]
        self.url = reverse("invoices:pdf_invoice", args=[self.invoice.pk])

    def test_detail_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_return_404_if_not_my_invoice(self):
        url = reverse("invoices:pdf_invoice", args=[self.other_invoice.pk])
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_return_pdf_if_logged(self):
        self.client.login(username=self.user.username, password="test")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "invoices/pdf_invoice.html")
        self.assertEqual(self.invoice.pk, response.context["invoice"].pk)
