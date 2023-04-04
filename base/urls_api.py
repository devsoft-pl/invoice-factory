from django.urls import include, path
from rest_framework import routers

from invoices import views_api

router = routers.DefaultRouter()
router.register(r"users", views_api.UserViewSet)
router.register(r"vat_rates", views_api.VatRateViewSet)
router.register(r"currencies", views_api.CurrencyViewSet)
router.register(r"countries", views_api.CountryViewSet)
router.register(r"companies", views_api.CompanyViewSet)
router.register(r"invoices", views_api.InvoiceViewSet)
router.register(r"items", views_api.ItemViewSet)


urlpatterns = [
    path("", include(router.urls)),
]
