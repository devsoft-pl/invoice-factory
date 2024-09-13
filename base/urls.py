from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

from base import urls_api
from invoices.views import faq_view, index_view, privacy_policy_view, terms_view

urlpatterns = [
    path("", index_view, name="index"),
    path("admin/", admin.site.urls),
    path("api/", include(urls_api)),
    path("api-token-auth/", obtain_auth_token),
    path("companies/", include("companies.urls")),
    path("countries/", include("countries.urls")),
    path("currencies/", include("currencies.urls")),
    path("invoices/", include("invoices.urls")),
    path("items/", include("items.urls")),
    path("users/", include("users.urls")),
    path("vat_rates/", include("vat_rates.urls")),
    path("reports/", include("reports.urls")),
    path("accountants/", include("accountants.urls")),
    path("summary_recipients/", include("summary_recipients.urls")),
    path("persons/", include("persons.urls")),
    path("faq/", faq_view, name="faq"),
    path("terms/", terms_view, name="terms"),
    path("privacy-policy/", privacy_policy_view, name="privacy_policy"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
