from django.core.mail import send_mail

from base.celery import app


@app.task()
def invoice_notification():
    pass
