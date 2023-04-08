from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

from base import urls_api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(urls_api)),
    path("api-token-auth/", obtain_auth_token),
    path("companies/", include("companies.urls")),
    path("countries/", include("countries.urls")),
    path("currencies/", include("currencies.urls")),
    path("invoices/", include("invoices.urls")),
    path("vat_rates/", include("vat_rates.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
