from django.urls import include, path
from rest_framework import routers

from accountants.views_api import AccountantViewSet
from companies.views_api import CompanyViewSet
from countries.views_api import CountryViewSet
from currencies.views_api import CurrencyViewSet
from invoices.views_api import InvoiceViewSet
from items.views_api import ItemViewSet
from summary_recipients.views_api import SummaryRecipientViewSet
from users.views_api import UserViewSet
from vat_rates.views_api import VatRateViewSet

router = routers.DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"vat_rates", VatRateViewSet)
router.register(r"currencies", CurrencyViewSet)
router.register(r"countries", CountryViewSet)
router.register(r"companies", CompanyViewSet)
router.register(r"invoices", InvoiceViewSet)
router.register(r"items", ItemViewSet)
router.register(r"accountants", AccountantViewSet)
router.register(r"summary_recipients", SummaryRecipientViewSet)


urlpatterns = [
    path("", include(router.urls)),
]
