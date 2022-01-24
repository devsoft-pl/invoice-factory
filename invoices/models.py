from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _


class VatRate(models.Model):
    rate = models.PositiveIntegerField(verbose_name=_('Rate'), unique=True)
    user = models.ForeignKey(User, verbose_name=_('User'), on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(self.rate)


class Currency(models.Model):
    code = models.CharField(verbose_name=_('Code'), max_length=10, unique=True)
    user = models.ForeignKey(User, verbose_name=_('User'), on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.code

    class Meta:
        verbose_name_plural = 'currencies'


class Company(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=100)
    nip = models.CharField(verbose_name=_('NIP'), max_length=12, unique=True)
    address = models.CharField(verbose_name=_('Address'), max_length=100)
    zip_code = models.CharField(verbose_name=_('ZIP Code'), max_length=10)
    city = models.CharField(verbose_name=_('City'), max_length=60)
    email = models.EmailField(verbose_name=_('Email'))
    phone_number = models.CharField(verbose_name=_('Phone number'), max_length=20, null=True, blank=True)
    user = models.ForeignKey(User, verbose_name=_('User'), on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'companies'


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

    company = models.ForeignKey(Company, verbose_name=_('Company'), on_delete=models.CASCADE, related_name='invoice')
    invoice_type = models.IntegerField(verbose_name=_('Invoice type'), choices=INVOICE_TYPES)
    payment_method = models.IntegerField(verbose_name=_('Payment method'), choices=PAYMENT_METHOD)
    create_date = models.DateField(verbose_name=_('Create date'), default=timezone.now, editable=True)
    sale_date = models.DateField(verbose_name=_('Sale date'), default=timezone.now, editable=True)
    payment_date = models.DateField(verbose_name=_('Payment date'), default=timezone.now, editable=True)
    account_number = models.CharField(verbose_name=_('Account number'), max_length=50, null=True, blank=True)
    invoice_number = models.CharField(verbose_name=_('Invoice number'), max_length=30)
    invoice_pdf = models.FileField(verbose_name=_('Invoice pdf'), null=True, blank=True)
    currency = models.ForeignKey(Currency, verbose_name=_('Currency'), on_delete=models.CASCADE, null=True,
                                 related_name='invoice')
    user = models.ForeignKey(User, verbose_name=_('User'), on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.invoice_number or f'#{self.id}'

    @property
    def net_amount(self):
        net_sum = 0
        for item in self.items.all():  # self.items ze wzgledy na related_name="items" w Item
            net_sum = net_sum + item.net_amount
        return net_sum

    @property
    def tax_amount(self):
        tax_sum = 0
        for item in self.items.all():
            tax_sum = tax_sum + item.tax_amount
        return tax_sum

    @property
    def gross_amount(self):
        gross_sum = 0
        for item in self.items.all():
            gross_sum = gross_sum + item.gross_amount
        return gross_sum


class Item(models.Model):
    KG = 0
    L = 1
    KM = 2
    HOUR = 3
    ITEM = 4

    UNIT_TYPES = (
        (KG, 'Kilogram'),
        (L, 'Liter'),
        (KM, 'Kilometer'),
        (HOUR, 'Hour'),
        (ITEM, 'Item')

    )

    invoice = models.ForeignKey(Invoice, verbose_name=_('Invoice'), on_delete=models.CASCADE, related_name="items")
    name = models.CharField(verbose_name=_('Name'), max_length=255)
    unit = models.IntegerField(verbose_name=_('Type of unit'), choices=UNIT_TYPES)
    amount = models.PositiveIntegerField(verbose_name=_('Amount'))
    net_price = models.PositiveIntegerField(verbose_name=_('Net price'))
    vat = models.ForeignKey(VatRate, verbose_name=_('Vat'), on_delete=models.CASCADE, related_name='item')
    user = models.ForeignKey(User, verbose_name=_('User'), on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name

    @property  # dekorator tworzy atrybut o nazwie taka jak nazwa funkcji
    def net_amount(self):
        return self.amount * self.net_price

    @property
    def tax_amount(self):
        return (self.net_amount * self.vat.rate)/100

    @property
    def gross_amount(self):
        return self.net_amount + self.tax_amount


