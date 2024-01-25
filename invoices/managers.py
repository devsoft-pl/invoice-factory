from django.db import models
from django.db.models import Sum
from django.db.models.functions import ExtractMonth


class InvoiceQuerySet(models.QuerySet):
    def sales(self):
        return self.filter(invoice_type=self.model.INVOICE_SALES)

    def with_months(self):
        return self.annotate(month=ExtractMonth("sale_date")).values("month")

    def with_sum(self, field):
        return self.annotate(sum=Sum(field))
