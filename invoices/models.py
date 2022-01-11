from django.db import models
from django.utils.translation import gettext as _


class VatRate(models.Model):
    rate = models.PositiveIntegerField(verbose_name=_('Rate'))

    def __str__(self):
        return str(self.rate)


class Currency(models.Model):
    code = models.CharField(verbose_name=_('Code'), max_length=10)
    symbol = models.CharField(verbose_name=_('Symbol'), max_length=10, null=True, blank=True)

    def __str__(self):
        return self.code


class Company(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=100)
    nip = models.CharField(verbose_name=_('NIP'), max_length=12, null=True, blank=True)
    street = models.CharField(verbose_name=_('Street'), max_length=100, null=True, blank=True)
    zip_code = models.CharField(verbose_name=_('ZIP Code'), max_length=10, null=True, blank=True)
    city = models.CharField(verbose_name=_('City'), max_length=60, null=True, blank=True)
    email = models.EmailField(verbose_name=_('Email'), null=True, blank=True)
    default_currency = models.ForeignKey(Currency, verbose_name=_('Default currency'), on_delete=models.CASCADE,
                                         null=True, blank=True)

    def __str__(self):
        return self.name


class Invoice(models.Model):
    INVOICE_SALES = 0
    INVOICE_PURCHASE = 1

    INVOICE_TYPES = (
        (INVOICE_SALES, 'Sales'),
        (INVOICE_PURCHASE, 'Purchase'),
    )

    BANK_TRANSFER = 0
    CASH_PAYMENT = 1

    PAYMENT_METHOD = (
        (BANK_TRANSFER, 'Transfer'),
        (CASH_PAYMENT, 'Cash'),
    )

    company = models.ForeignKey(Company, verbose_name=_('Company'), on_delete=models.CASCADE)
    invoice_type = models.IntegerField(verbose_name=_('Invoice type'), choices=INVOICE_TYPES, null=True, blank=True)
    payment_method = models.IntegerField(verbose_name=_('Payment method'), choices=PAYMENT_METHOD, null=True,
                                         blank=True)
    create_date = models.DateField(verbose_name=_('Create date'), null=True, blank=True)
    sale_date = models.DateField(verbose_name=_('Sale date'), null=True, blank=True)
    payment_date = models.DateField(verbose_name=_('Payment date'), null=True, blank=True)
    invoice_number = models.CharField(verbose_name=_('Invoice number'), max_length=30, null=True, blank=True)
    invoice_pdf = models.FileField(verbose_name=_('Invoice pdf'), null=True, blank=True)
    currency = models.ForeignKey(Currency, verbose_name=_('Currency'), on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.invoice_number or f'#{self.id}'

    @property
    def net_amount(self):
        net_sum = 0
        for item in self.item_set.all():
            net_sum = net_sum + item.net_amount
        return net_sum

    @property
    def tax_amount(self):
        tax_sum = 0
        for item in self.item_set.all():
            tax_sum = tax_sum + item.tax_amount
        return tax_sum

    @property
    def gross_amount(self):
        gross_sum = 0
        for item in self.item_set.all():
            gross_sum = gross_sum + item.gross_amount
        return gross_sum


class Item(models.Model):
    invoice = models.ForeignKey(Invoice, verbose_name=_('Invoice'), on_delete=models.CASCADE)
    name = models.CharField(verbose_name=_('Name'), max_length=255)
    amount = models.PositiveIntegerField(verbose_name=_('Amount'))
    net_price = models.PositiveIntegerField(verbose_name=_('Net price'))
    vat = models.ForeignKey(VatRate, verbose_name=_('Vat'), on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    @property
    def net_amount(self):
        return self.amount * self.net_price

    @property
    def tax_amount(self):
        return (self.net_amount * self.vat.rate)/100

    @property
    def gross_amount(self):
        return self.net_amount + self.tax_amount
