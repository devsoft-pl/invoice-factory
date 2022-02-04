from base.celery import app

from django.core.mail import send_mail


@app.task()
def invoice_notification():
    pass
