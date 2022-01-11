from django.urls import (
    include,
    path,
)
from rest_framework import routers
from invoices import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'vat_rates', views.VatRateViewSet)
router.register(r'currencies', views.CurrencyViewSet)
router.register(r'companies', views.CompanyViewSet)
router.register(r'invoices', views.InvoiceViewSet)
router.register(r'items', views.ItemViewSet)


urlpatterns = [
    path('', include(router.urls)),

]






