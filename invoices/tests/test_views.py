import datetime
from unittest.mock import patch

from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.urls import reverse
from parameterized import parameterized

from companies.factories import CompanyFactory
from currencies.factories import CurrencyFactory
from invoices.factories import (
    InvoiceBuyDictFactory,
    InvoiceBuyFactory,
    InvoiceSellDictFactory,
    InvoiceSellFactory,
    InvoiceSellPersonFactory,
    InvoiceSellPersonToClientFactory,
)
from invoices.models import CorrectionInvoiceRelation, Invoice
from invoices.views import clone, create_correction_invoice_number
from items.factories import ItemFactory
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
                12, company__user=self.user, currency=self.currency, is_settled=False
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

    def test_detail_sell_if_logged_when_is_issued_by_my_company(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "invoices/detail_sell_invoice.html")
        self.assertEqual(self.sell_invoice.pk, response.context["invoice"].pk)

    def test_details_sales_invoice_if_logged_when_is_issued_by_person(self):
        self.client.login(username=self.user.email, password="test")

        invoice = InvoiceSellPersonToClientFactory.create(
            person__user=self.user, currency=self.currency, is_settled=False
        )
        url = reverse("invoices:detail_invoice", args=[invoice.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "invoices/detail_sell_invoice.html")
        self.assertEqual(invoice.pk, response.context["invoice"].pk)

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

    def test_return_404_if_invoice_is_not_issued_by_company_or_person(self):
        self.client.login(username=self.user.email, password="test")

        other_sell_invoice = InvoiceSellPersonToClientFactory()
        url = reverse("invoices:detail_invoice", args=[other_sell_invoice.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_raise_exception_if_invoice_is_not_issued_by_company_or_person(self):
        self.client.login(username=self.user.email, password="test")

        invoice = InvoiceSellPersonFactory(company=None, person=None)
        url = reverse("invoices:detail_invoice", args=[invoice.pk])

        with self.assertRaises(Exception) as context:
            self.client.get(url)
        self.assertEqual(str(context.exception), "This should not have happened")


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

    def test_return_404_if_invoice_is_not_issued_by_company_or_person(self):
        self.client.login(username=self.user.email, password="test")

        other_sell_invoice = InvoiceSellPersonToClientFactory()
        url = reverse("invoices:delete_invoice", args=[other_sell_invoice.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_raise_exception_if_invoice_is_not_issued_by_company_or_person(self):
        self.client.login(username=self.user.email, password="test")

        invoice = InvoiceSellPersonFactory(company=None, person=None)
        url = reverse("invoices:delete_invoice", args=[invoice.pk])

        with self.assertRaises(Exception) as context:
            self.client.get(url)
        self.assertEqual(str(context.exception), "This should not have happened")


class TestCreateSellInvoice(TestInvoice):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("invoices:create_sell_invoice")
        self.company = CompanyFactory.create(user=self.user, is_my_company=True)
        self.contractor = CompanyFactory.create(user=self.user, is_my_company=False)
        self.person = PersonFactory.create(user=self.user)
        self.currency = CurrencyFactory.create(user=self.user)

    def test_create_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_create_invalid_form_display_errors_for_client(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "company", "This field is required."
        )
        self.assertFormError(
            response.context["form"], "client", "This field is required."
        )
        self.assertFormError(
            response.context["form"], "create_date", "This field is required."
        )
        self.assertFormError(
            response.context["form"], "currency", "This field is required."
        )
        self.assertTemplateUsed(response, "invoices/create_sell_invoice.html")

    def test_create_invalid_form_display_errors_for_person(self):
        self.client.login(username=self.user.email, password="test")

        url = reverse("invoices:create_sell_person_invoice")
        response = self.client.post(url, {})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "invoices/create_sell_person_invoice.html")
        self.assertFormError(
            response.context["form"], "company", "This field is required."
        )
        self.assertFormError(
            response.context["form"], "person", "This field is required."
        )
        self.assertFormError(
            response.context["form"], "create_date", "This field is required."
        )
        self.assertFormError(
            response.context["form"], "currency", "This field is required."
        )

    def test_create_invalid_form_display_errors_for_person_to_client(self):
        self.client.login(username=self.user.email, password="test")

        url = reverse("invoices:create_sell_person_to_client_invoice")
        response = self.client.post(url, {})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "invoices/create_sell_person_to_client_invoice.html"
        )
        self.assertFormError(
            response.context["form"], "person", "This field is required."
        )
        self.assertFormError(
            response.context["form"], "client", "This field is required."
        )
        self.assertFormError(
            response.context["form"], "create_date", "This field is required."
        )
        self.assertFormError(
            response.context["form"], "currency", "This field is required."
        )

    def test_create_with_valid_data_for_client(self):
        self.client.login(username=self.user.email, password="test")

        data = InvoiceSellDictFactory(
            is_recurring="",
            invoice_number="1/01/2023",
            company=self.company.pk,
            client=self.contractor.pk,
            account_number="111111111111111",
            currency=self.currency.pk,
            is_last_day="",
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
                is_recurring=False,
            ).exists()
        )
        self.assertEqual(
            Invoice.objects.filter(
                invoice_number=data["invoice_number"],
                company__user=self.user,
                is_recurring=False,
            ).count(),
            invoices_before_create + 1,
        )

    def test_create_with_valid_data_for_person(self):
        self.client.login(username=self.user.email, password="test")

        data = InvoiceSellDictFactory(
            invoice_number="1/01/2023",
            company=self.company.pk,
            person=self.person.pk,
            currency=self.currency.pk,
            account_number="111111111111111",
            is_recurring="",
            is_last_day="",
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

    def test_create_with_valid_data_for_person_to_client(self):
        self.client.login(username=self.user.email, password="test")

        data = InvoiceSellDictFactory(
            invoice_number="1/01/2023",
            client=self.contractor.pk,
            person=self.person.pk,
            currency=self.currency.pk,
            account_number="111111111111111",
            is_recurring="",
            is_last_day="",
        )
        invoices_before_create = Invoice.objects.filter(
            invoice_number=data["invoice_number"],
            person__user=self.user,
        ).count()

        url = reverse("invoices:create_sell_person_to_client_invoice")

        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("invoices:list_invoices"))
        self.assertTrue(
            Invoice.objects.filter(
                invoice_number=data["invoice_number"], person__user=self.user
            ).exists()
        )
        self.assertEqual(
            Invoice.objects.filter(
                invoice_number=data["invoice_number"],
                person__user=self.user,
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

    def test_get_form_for_person_to_client(self):
        self.client.login(username=self.user.email, password="test")

        url = reverse("invoices:create_sell_person_to_client_invoice")
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
            response.context["form"], "invoice_number", "This field is required."
        )
        self.assertFormError(
            response.context["form"], "sale_date", "This field is required."
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
            response.context["form"], "company", "This field is required."
        )
        self.assertFormError(
            response.context["form"], "client", "This field is required."
        )
        self.assertFormError(
            response.context["form"], "create_date", "This field is required."
        )
        self.assertFormError(
            response.context["form"], "currency", "This field is required."
        )
        self.assertTemplateUsed(response, "invoices/replace_sell_invoice.html")

    def test_replace_invalid_form_display_errors_for_person(self):
        self.client.login(username=self.user.email, password="test")

        person_invoice = InvoiceSellPersonFactory.create(
            company__user=self.user, is_settled=False
        )

        url = reverse("invoices:replace_sell_invoice", args=[person_invoice.pk])
        response = self.client.post(url, {})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "invoices/replace_sell_invoice.html")
        self.assertFormError(
            response.context["form"], "company", "This field is required."
        )
        self.assertFormError(
            response.context["form"], "person", "This field is required."
        )
        self.assertFormError(
            response.context["form"], "create_date", "This field is required."
        )
        self.assertFormError(
            response.context["form"], "currency", "This field is required."
        )

    def test_replace_with_valid_data_for_client(
        self,
    ):
        self.client.login(username=self.user.email, password="test")

        data = InvoiceSellDictFactory(
            invoice_number="2/05/2023",
            company=self.company.pk,
            client=self.contractor.pk,
            currency=self.currency.pk,
            account_number="111111111111111",
            is_recurring="",
            is_last_day="",
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

        person_invoice = InvoiceSellPersonFactory.create(
            company__user=self.user, is_settled=False
        )
        person = PersonFactory.create(user=self.user)

        data = InvoiceSellDictFactory(
            invoice_number="2/06/2023",
            company=self.company.pk,
            person=person.pk,
            currency=self.currency.pk,
            account_number="111111111111111",
            is_recurring="",
            is_last_day="",
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

    def test_return_404_if_invoice_is_settled_and_is_replace(self):
        self.client.login(username=self.user.email, password="test")

        invoice = InvoiceSellFactory.create(is_settled=True)
        url = reverse("invoices:replace_sell_invoice", args=[invoice.pk])

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
        invoice = InvoiceSellFactory.create(invoice_number="1/03/2024")

        assert create_correction_invoice_number(invoice) == "1/03/2024/k"

    def test_crete_correction_invoice_if_is_not_settled(
        self,
    ):
        self.client.login(username=self.user.email, password="test")
        invoice = InvoiceSellFactory.create(
            invoice_number="1/03/2024",
            company=self.company,
            client=self.contractor,
            currency=self.currency,
            account_number="111111111111111",
            is_settled=False,
            is_recurring=False,
            is_last_day=False,
        )

        url = reverse("invoices:create_correction_invoice", args=[invoice.pk])

        response = self.client.get(url)

        form = response.context["form"]
        form.initial["is_recurring"] = ""
        form.initial["is_last_day"] = ""
        response = self.client.post(url, data=form.initial)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("invoices:list_invoices"))

        self.assertTrue(
            CorrectionInvoiceRelation.objects.filter(
                invoice=invoice, correction_invoice__invoice_number="1/03/2024/k"
            ).exists()
        )

    def test_crete_correction_invoice_if_is_settled(self):
        self.client.login(username=self.user.email, password="test")
        invoice = InvoiceSellFactory.create(
            invoice_number="1/03/2024",
            company=self.company,
            client=self.contractor,
            currency=self.currency,
            account_number="111111111111111",
            is_settled=True,
        )

        url = reverse("invoices:create_correction_invoice", args=[invoice.pk])

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class TestDuplicateCompanyInvoice(TestInvoice):
    def setUp(self) -> None:
        super().setUp()
        self.invoice = self.user_sales_invoices[0]
        self.company = CompanyFactory.create(user=self.user, is_my_company=True)
        self.contractor = CompanyFactory.create(user=self.user, is_my_company=False)
        self.currency = CurrencyFactory.create(user=self.user)
        self.url = reverse("invoices:duplicate_company_invoice", args=[self.invoice.pk])

    def test_duplicate_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_return_404_if_not_my_invoice(self):
        self.client.login(username=self.user.email, password="test")

        url = reverse(
            "invoices:duplicate_company_invoice", args=[self.other_sell_invoice.pk]
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    @patch("invoices.tasks.datetime")
    def test_duplicate_company_for_person(self, datetime_mock):
        self.client.login(username=self.user.email, password="test")
        datetime_mock.today.return_value = datetime.date(2025, 5, 28)
        person = PersonFactory.create(user=self.user)
        invoice = InvoiceSellPersonFactory.create(
            invoice_number="1/03/2024",
            company=self.company,
            person=person,
            currency=self.currency,
            account_number="111111111111111",
            is_recurring=False,
        )
        ItemFactory.create(invoice=invoice)

        url = reverse("invoices:duplicate_company_invoice", args=[invoice.pk])

        response = self.client.get(url)

        new_invoice = response.context["invoice"]
        self.assertEqual(new_invoice.invoice_number, "1/06/2025")
        self.assertEqual(new_invoice.items.count(), 1)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "invoices/replace_sell_invoice.html")

    @patch("invoices.tasks.datetime")
    def test_duplicate_company_for_contractor(self, datetime_mock):
        self.client.login(username=self.user.email, password="test")
        datetime_mock.today.return_value = datetime.date(2025, 5, 28)
        invoice = InvoiceSellFactory.create(
            invoice_number="1/03/2024",
            company=self.company,
            client=self.contractor,
            currency=self.currency,
            account_number="111111111111111",
            is_recurring=False,
        )
        ItemFactory.create(invoice=invoice)

        url = reverse("invoices:duplicate_company_invoice", args=[invoice.pk])

        response = self.client.get(url)

        new_invoice = response.context["invoice"]
        self.assertEqual(new_invoice.invoice_number, "1/06/2025")
        self.assertEqual(new_invoice.items.count(), 1)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "invoices/replace_sell_invoice.html")

    def test_no_duplicate_company_invoice_if_is_recurring(self):
        self.client.login(username=self.user.email, password="test")
        invoice = InvoiceSellFactory.create(
            invoice_number="1/03/2024",
            company=self.company,
            client=self.contractor,
            currency=self.currency,
            account_number="111111111111111",
            is_recurring=True,
        )

        url = reverse("invoices:duplicate_company_invoice", args=[invoice.pk])

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class TestDuplicateIndividualInvoice(TestInvoice):
    def setUp(self) -> None:
        super().setUp()
        self.currency = CurrencyFactory.create(user=self.user)
        self.person = PersonFactory.create(user=self.user)
        self.contractor = CompanyFactory.create(user=self.user, is_my_company=False)
        self.invoice = InvoiceSellPersonToClientFactory.create(
            invoice_number="1/03/2024",
            person=self.person,
            client=self.contractor,
            currency=self.currency,
            account_number="111111111111111",
            is_recurring=False,
        )

        self.url = reverse(
            "invoices:duplicate_individual_invoice", args=[self.invoice.pk]
        )

    def test_duplicate_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_return_404_if_not_my_invoice(self):
        self.client.login(username=self.user.email, password="test")

        invoice = InvoiceSellPersonToClientFactory()

        url = reverse("invoices:duplicate_individual_invoice", args=[invoice.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    @patch("invoices.tasks.datetime")
    def test_duplicate_individual_for_contractor(self, datetime_mock):
        self.client.login(username=self.user.email, password="test")
        datetime_mock.today.return_value = datetime.date(2025, 5, 28)

        ItemFactory.create(invoice=self.invoice)

        response = self.client.get(self.url)

        new_invoice = response.context["invoice"]
        self.assertEqual(new_invoice.invoice_number, "1/06/2025")
        self.assertEqual(new_invoice.items.count(), 1)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "invoices/replace_sell_person_to_client_invoice.html"
        )

    def test_no_duplicate_individual_invoice_if_is_recurring(self):
        self.client.login(username=self.user.email, password="test")
        invoice = InvoiceSellPersonToClientFactory.create(
            invoice_number="1/03/2024",
            person=self.person,
            client=self.contractor,
            currency=self.currency,
            account_number="111111111111111",
            is_recurring=True,
        )

        url = reverse("invoices:duplicate_individual_invoice", args=[invoice.pk])

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class TestReplaceSellPersonToClientInvoice(TestInvoice):
    def setUp(self) -> None:
        super().setUp()
        self.currency = CurrencyFactory.create(user=self.user)
        self.person = PersonFactory.create(user=self.user)
        self.contractor = CompanyFactory.create(user=self.user, is_my_company=False)
        self.invoice = InvoiceSellPersonToClientFactory.create(
            person__user=self.user,
            client=self.contractor,
            currency=self.currency,
            is_settled=False,
        )
        self.url = reverse(
            "invoices:replace_sell_person_to_client_invoice", args=[self.invoice.pk]
        )

    def test_replace_if_not_logged(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_replace_invalid_form_display_errors(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "invoices/replace_sell_person_to_client_invoice.html"
        )
        self.assertFormError(
            response.context["form"], "person", "This field is required."
        )
        self.assertFormError(
            response.context["form"], "client", "This field is required."
        )
        self.assertFormError(
            response.context["form"], "create_date", "This field is required."
        )
        self.assertFormError(
            response.context["form"], "currency", "This field is required."
        )

    def test_replace_with_valid_data(self):
        self.client.login(username=self.user.email, password="test")

        data = InvoiceSellDictFactory(
            invoice_number="2/06/2023",
            person=self.person.pk,
            client=self.contractor.pk,
            currency=self.currency.pk,
            account_number="111111111111111",
            is_recurring="",
            is_last_day="",
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
                person__user=self.user,
            ).exists()
        )

    def test_return_404_if_not_my_invoice(self):
        self.client.login(username=self.user.email, password="test")

        invoice = InvoiceSellPersonToClientFactory()

        url = reverse(
            "invoices:replace_sell_person_to_client_invoice", args=[invoice.pk]
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_raise_exception_if_invoice_is_not_issued_by_person_or_client(self):
        self.client.login(username=self.user.email, password="test")

        invoice = InvoiceSellPersonToClientFactory(person=None)
        url = reverse(
            "invoices:replace_sell_person_to_client_invoice", args=[invoice.pk]
        )

        with self.assertRaises(Exception) as context:
            self.client.get(url)
        self.assertEqual(str(context.exception), "This should not have happened")

    def test_return_404_if_invoice_is_settled_and_is_replace(self):
        self.client.login(username=self.user.email, password="test")

        invoice = InvoiceSellPersonToClientFactory.create(
            person=self.person, is_settled=True
        )
        url = reverse(
            "invoices:replace_sell_person_to_client_invoice", args=[invoice.pk]
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_get_form(self):
        self.client.login(username=self.user.email, password="test")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_create_correction_invoice_number(self):
        invoice = InvoiceSellPersonToClientFactory.create(invoice_number="1/03/2024")

        assert create_correction_invoice_number(invoice) == "1/03/2024/k"

    def test_crete_correction_invoice_if_is_not_settled(
        self,
    ):
        self.client.login(username=self.user.email, password="test")
        invoice = InvoiceSellPersonToClientFactory.create(
            invoice_number="1/03/2024",
            person=self.person,
            client=self.contractor,
            currency=self.currency,
            account_number="111111111111111",
            is_settled=False,
            is_recurring=False,
            is_last_day=False,
        )

        url = reverse(
            "invoices:create_correction_person_to_client_invoice", args=[invoice.pk]
        )

        response = self.client.get(url)

        form = response.context["form"]
        form.initial["is_recurring"] = ""
        form.initial["is_last_day"] = ""
        response = self.client.post(url, data=form.initial)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("invoices:list_invoices"))

        self.assertTrue(
            CorrectionInvoiceRelation.objects.filter(
                invoice=invoice, correction_invoice__invoice_number="1/03/2024/k"
            ).exists()
        )

    def test_crete_correction_invoice_if_is_settled(self):
        self.client.login(username=self.user.email, password="test")
        invoice = InvoiceSellPersonToClientFactory.create(
            invoice_number="1/03/2024",
            person=self.person,
            client=self.contractor,
            currency=self.currency,
            account_number="111111111111111",
            is_settled=True,
        )

        url = reverse(
            "invoices:create_correction_person_to_client_invoice", args=[invoice.pk]
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


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
            response.context["form"], "sale_date", "This field is required."
        )
        self.assertTemplateUsed(response, "invoices/replace_buy_invoice.html")

    def test_replace_with_valid_data(self):
        self.client.login(username=self.user.email, password="test")

        data = InvoiceBuyDictFactory(
            company=self.company.pk,
            invoice_number="2/03/2023",
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

    def test_return_404_if_invoice_is_not_issued_by_company_or_person(self):
        self.client.login(username=self.user.email, password="test")

        other_sell_invoice = InvoiceSellPersonToClientFactory()
        url = reverse("invoices:pdf_invoice", args=[other_sell_invoice.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_raise_exception_if_invoice_is_not_issued_by_company_or_person(self):
        self.client.login(username=self.user.email, password="test")

        invoice = InvoiceSellPersonToClientFactory(client=None, person=None)
        url = reverse("invoices:pdf_invoice", args=[invoice.pk])

        with self.assertRaises(Exception) as context:
            self.client.get(url)
        self.assertEqual(str(context.exception), "This should not have happened")

    def test_return_errors_when_pisa_failed(self):
        self.client.login(username=self.user.email, password="test")

        with patch("invoices.views.pisa.CreatePDF") as mock_pisa:
            mock_pisa.return_value.err = True
            response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "We had some errors")
