from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.authtoken.views import obtain_auth_token

from base import urls_api
from invoices.views import index_view

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
    path("faq/", TemplateView.as_view(template_name="faq.html"), name="faq"),
    path("terms/", TemplateView.as_view(template_name="terms.html"), name="terms"),
    path(
        "privacy-policy/",
        TemplateView.as_view(template_name="privacy_policy.html"),
        name="privacy_policy",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
