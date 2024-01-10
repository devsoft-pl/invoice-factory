from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.urls import reverse
from parameterized import parameterized

from companies.factories import CompanyFactory
from currencies.factories import CurrencyFactory
from invoices.factories import (InvoiceBuyDictFactory, InvoiceBuyFactory,
                                InvoiceSellDictFactory, InvoiceSellFactory,
                                InvoiceSellPersonFactory)
from invoices.models import CorrectionInvoiceRelation, Invoice
from invoices.views import clone, create_correction_invoice_number
from persons.factories import PersonFactory
from users.factories import UserFactory


class TestInvoice(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.set_password("test")
        self.user.save()
        self.currency = CurrencyFactory.create(code="PLN")
        self.user_sales_invoices = sorted(
            InvoiceSellFactory.create_batch(
                12, company__user=self.user, currency=self.currency
            ),
            key=lambda invoice: invoice.sale_date,
            reverse=True,
        )
        self.user_buy_invoices = sorted(
            InvoiceBuyFactory.create_batch(12, company__user=self.user),
            key=lambda invoice: invoice.sale_date,
            reverse=True,
        )
        self.other_sell_invoice = InvoiceSellFactory()


class TestListInvoices(TestInvoice):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("invoices:list_invoices")

    def test_list_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_list_if_logged(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        object_list = response.context["invoices"]

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "invoices/list_invoices.html")
        self.assertTrue(len(object_list) == 10)
        self.assertListEqual(
            list(object_list),
            list(Invoice.objects.filter(company__user=self.user)[:10]),
        )

    def test_returns_first_page_when_abc(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(f"{self.url}?page=abc")

        object_list = response.context["invoices"]

        self.assertListEqual(
            list(object_list),
            list(Invoice.objects.filter(company__user=self.user)[:10]),
        )

    @parameterized.expand([[3], [666]])
    def test_pagination_return_correct_list(self, page):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(f"{self.url}?page={page}")

        object_list = response.context["invoices"]

        self.assertTrue(len(object_list) == 4)


class TestDetailInvoice(TestInvoice):
    def setUp(self) -> None:
        super().setUp()
        self.sell_invoice = self.user_sales_invoices[0]
        self.url = reverse("invoices:detail_invoice", args=[self.sell_invoice.pk])

    def test_detail_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_detail_sell_if_logged(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "invoices/detail_sell_invoice.html")
        self.assertEqual(self.sell_invoice.pk, response.context["invoice"].pk)

    def test_detail_buy_if_logged(self):
        self.client.login(username=self.user.email, password="test")

        buy_invoice = self.user_buy_invoices[0]
        url = reverse("invoices:detail_invoice", args=[buy_invoice.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "invoices/detail_buy_invoice.html")
        self.assertEqual(buy_invoice.pk, response.context["invoice"].pk)

    def test_return_404_if_not_my_invoice(self):
        self.client.login(username=self.user.email, password="test")

        other_sell_invoice = InvoiceSellFactory()
        url = reverse("invoices:detail_invoice", args=[other_sell_invoice.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)


class TestDeleteInvoice(TestInvoice):
    def setUp(self) -> None:
        super().setUp()
        self.invoice = self.user_sales_invoices[0]
        self.url = reverse("invoices:delete_invoice", args=[self.invoice.pk])

    def test_delete_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_delete_if_logged(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        with self.assertRaises(ObjectDoesNotExist):
            Invoice.objects.get(pk=self.invoice.pk)
        self.assertEqual(response.status_code, 302)

    def test_return_404_if_not_my_invoice(self):
        self.client.login(username=self.user.email, password="test")

        url = reverse("invoices:delete_invoice", args=[self.other_sell_invoice.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)


class TestCreateSellInvoice(TestInvoice):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("invoices:create_sell_invoice")
        self.company = CompanyFactory.create(user=self.user, is_my_company=True)
        self.contractor = CompanyFactory.create(user=self.user, is_my_company=False)
        self.currency = CurrencyFactory.create(user=self.user)

    def test_create_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_create_invalid_form_display_errors_for_client(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "company", "To pole jest wymagane."
        )
        self.assertFormError(
            response.context["form"], "create_date", "To pole jest wymagane."
        )
        self.assertFormError(
            response.context["form"], "currency", "To pole jest wymagane."
        )
        self.assertTemplateUsed(response, "invoices/create_sell_invoice.html")

    def test_create_invalid_form_display_errors_for_person(self):
        self.client.login(username=self.user.email, password="test")

        url = reverse("invoices:create_sell_person_invoice")
        response = self.client.post(url, {})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "invoices/create_sell_person_invoice.html")
        self.assertFormError(
            response.context["form"], "company", "To pole jest wymagane."
        )
        self.assertFormError(
            response.context["form"], "create_date", "To pole jest wymagane."
        )
        self.assertFormError(
            response.context["form"], "currency", "To pole jest wymagane."
        )

    def test_create_with_valid_data_for_client(self):
        self.client.login(username=self.user.email, password="test")

        data = InvoiceSellDictFactory(
            invoice_number="1/2023",
            company=self.company.pk,
            client=self.contractor.pk,
            currency=self.currency.pk,
            account_number="111111111111111",
        )
        invoices_before_create = Invoice.objects.filter(
            invoice_number=data["invoice_number"],
            company__user=self.user,
        ).count()

        response = self.client.post(self.url, data=data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("invoices:list_invoices"))
        self.assertTrue(
            Invoice.objects.filter(
                invoice_number=data["invoice_number"],
                company__user=self.user,
            ).exists()
        )
        self.assertEqual(
            Invoice.objects.filter(
                invoice_number=data["invoice_number"],
                company__user=self.user,
            ).count(),
            invoices_before_create + 1,
        )

    def test_create_with_valid_data_for_person(self):
        self.client.login(username=self.user.email, password="test")

        person = PersonFactory.create(user=self.user)
        data = InvoiceSellDictFactory(
            invoice_number="1/2023",
            company=self.company.pk,
            person=person.pk,
            currency=self.currency.pk,
            account_number="111111111111111",
        )
        invoices_before_create = Invoice.objects.filter(
            invoice_number=data["invoice_number"],
            company__user=self.user,
        ).count()

        url = reverse("invoices:create_sell_person_invoice")
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("invoices:list_invoices"))
        self.assertTrue(
            Invoice.objects.filter(
                invoice_number=data["invoice_number"],
                company__user=self.user,
            ).exists()
        )
        self.assertEqual(
            Invoice.objects.filter(
                invoice_number=data["invoice_number"],
                company__user=self.user,
            ).count(),
            invoices_before_create + 1,
        )

    def test_get_form_for_client(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_get_form_for_person(self):
        self.client.login(username=self.user.email, password="test")

        url = reverse("invoices:create_sell_person_invoice")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)


class TestCreateBuyInvoice(TestInvoice):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("invoices:create_buy_invoice")
        self.company = CompanyFactory.create(user=self.user, is_my_company=True)

    def test_create_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_create_invalid_form_display_errors(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "invoice_number", "To pole jest wymagane."
        )
        self.assertFormError(
            response.context["form"], "sale_date", "To pole jest wymagane."
        )
        self.assertTemplateUsed(response, "invoices/create_buy_invoice.html")

    def test_create_with_valid_data(self):
        self.client.login(username=self.user.email, password="test")

        data = InvoiceBuyDictFactory(
            company=self.company.pk,
            invoice_number="1/2023",
        )
        files = {"invoice_file": data["invoice_file"]}
        invoices_before_create = Invoice.objects.filter(
            invoice_number=data["invoice_number"],
            sale_date=data["sale_date"],
            company__user=self.user,
        ).count()

        response = self.client.post(self.url, data=data, files=files)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("invoices:list_invoices"))
        self.assertTrue(
            Invoice.objects.filter(
                invoice_number=data["invoice_number"],
                sale_date=data["sale_date"],
                company__user=self.user,
            ).exists()
        )
        self.assertEqual(
            Invoice.objects.filter(
                invoice_number=data["invoice_number"],
                sale_date=data["sale_date"],
                company__user=self.user,
            ).count(),
            invoices_before_create + 1,
        )

    def test_get_form(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)


class TestReplaceSellInvoice(TestInvoice):
    def setUp(self) -> None:
        super().setUp()
        self.invoice = self.user_sales_invoices[0]
        self.url = reverse("invoices:replace_sell_invoice", args=[self.invoice.pk])
        self.company = CompanyFactory.create(user=self.user, is_my_company=True)
        self.contractor = CompanyFactory.create(user=self.user, is_my_company=False)
        self.currency = CurrencyFactory.create(user=self.user)

    def test_replace_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_replace_invalid_form_display_errors_for_client(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "company", "To pole jest wymagane."
        )
        self.assertFormError(
            response.context["form"], "create_date", "To pole jest wymagane."
        )
        self.assertFormError(
            response.context["form"], "currency", "To pole jest wymagane."
        )
        self.assertTemplateUsed(response, "invoices/replace_sell_invoice.html")

    def test_replace_invalid_form_display_errors_for_person(self):
        self.client.login(username=self.user.email, password="test")

        person_invoice = InvoiceSellPersonFactory.create(company__user=self.user)

        url = reverse("invoices:replace_sell_invoice", args=[person_invoice.pk])
        response = self.client.post(url, {})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "invoices/replace_sell_invoice.html")
        self.assertFormError(
            response.context["form"], "company", "To pole jest wymagane."
        )
        self.assertFormError(
            response.context["form"], "create_date", "To pole jest wymagane."
        )
        self.assertFormError(
            response.context["form"], "currency", "To pole jest wymagane."
        )

    def test_replace_with_valid_data_for_client(self):
        self.client.login(username=self.user.email, password="test")

        data = InvoiceSellDictFactory(
            invoice_number="2/2023",
            company=self.company.pk,
            client=self.contractor.pk,
            currency=self.currency.pk,
            account_number="111111111111111",
        )

        response = self.client.post(self.url, data=data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse("invoices:detail_invoice", args=[self.invoice.pk])
        )
        self.assertTrue(
            Invoice.objects.filter(
                invoice_number=data["invoice_number"],
                create_date=data["create_date"],
                currency=data["currency"],
                company__user=self.user,
            ).exists()
        )

    def test_replace_with_valid_data_for_person(self):
        self.client.login(username=self.user.email, password="test")

        person_invoice = InvoiceSellPersonFactory.create(company__user=self.user)
        person = PersonFactory.create(user=self.user)

        data = InvoiceSellDictFactory(
            invoice_number="2/2023",
            company=self.company.pk,
            person=person.pk,
            currency=self.currency.pk,
            account_number="111111111111111",
        )

        url = reverse("invoices:replace_sell_invoice", args=[person_invoice.pk])
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse("invoices:detail_invoice", args=[person_invoice.pk])
        )
        self.assertTrue(
            Invoice.objects.filter(
                invoice_number=data["invoice_number"],
                create_date=data["create_date"],
                currency=data["currency"],
                company__user=self.user,
            ).exists()
        )

    def test_return_404_if_not_my_invoice(self):
        self.client.login(username=self.user.email, password="test")

        url = reverse(
            "invoices:replace_sell_invoice", args=[self.other_sell_invoice.pk]
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_get_form(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_clone_returns_another_object(self):
        invoice = InvoiceSellFactory.create()

        assert clone(invoice).pk != invoice.pk

    def test_create_correction_invoice_number(self):
        invoice = InvoiceSellFactory.create(invoice_number="1/2024")

        assert create_correction_invoice_number(invoice) == "1/k/2024"

    def test_crete_correction_invoice(self):
        self.client.login(username=self.user.email, password="test")

        company = CompanyFactory.create(user=self.user, is_my_company=True)
        client = CompanyFactory.create(user=self.user, is_my_company=False)
        invoice = InvoiceSellFactory.create(
            invoice_number="1/2024",
            company=company,
            client=client,
            currency=self.currency,
            account_number="111111111111111",
        )

        url = reverse("invoices:create_correction_invoice", args=[invoice.pk])

        response = self.client.get(url)

        form = response.context["form"]
        response = self.client.post(url, data=form.initial)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("invoices:list_invoices"))
        self.assertTrue(
            CorrectionInvoiceRelation.objects.filter(
                invoice=invoice, correction_invoice__invoice_number="1/k/2024"
            ).exists()
        )


class TestReplaceBuyInvoice(TestInvoice):
    def setUp(self) -> None:
        super().setUp()
        self.invoice = self.user_buy_invoices[0]
        self.url = reverse("invoices:replace_buy_invoice", args=[self.invoice.pk])
        self.company = CompanyFactory.create(user=self.user, is_my_company=True)

    def test_replace_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_replace_invalid_form_display_errors(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "sale_date", "To pole jest wymagane."
        )
        self.assertTemplateUsed(response, "invoices/replace_buy_invoice.html")

    def test_replace_with_valid_data(self):
        self.client.login(username=self.user.email, password="test")

        data = InvoiceBuyDictFactory(
            company=self.company.pk,
            invoice_number="2/2023",
        )
        files = {"invoice_file": data["invoice_file"]}

        response = self.client.post(self.url, data=data, files=files)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse("invoices:detail_invoice", args=[self.invoice.pk])
        )
        self.assertTrue(
            Invoice.objects.filter(
                invoice_number=data["invoice_number"],
                sale_date=data["sale_date"],
                company__user=self.user,
            ).exists()
        )

    def test_return_404_if_not_my_invoice(self):
        self.client.login(username=self.user.email, password="test")

        url = reverse("invoices:replace_buy_invoice", args=[self.other_sell_invoice.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_get_form(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)


class TestPdfInvoice(TestInvoice):
    def setUp(self) -> None:
        super().setUp()
        self.invoice = self.user_sales_invoices[0]
        self.url = reverse("invoices:pdf_invoice", args=[self.invoice.pk])

    def test_detail_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_return_pdf_if_logged(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "invoices/pdf_invoice.html")
        self.assertEqual(self.invoice.pk, response.context["invoice"].pk)

    def test_return_404_if_not_my_invoice(self):
        self.client.login(username=self.user.email, password="test")

        url = reverse("invoices:pdf_invoice", args=[self.other_sell_invoice.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
