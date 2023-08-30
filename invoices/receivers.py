from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils.text import format_lazy as _


@receiver(post_save, sender=User)
def send_welcome_email(sender, instance: User, created=False, **kwargs):
    if created and instance.email:
        subject = _(f"Welcome in Invoice Manager")
        content = _(
            "Thanks for your registration. Your account details: \n "
            "Login: {username} \n"
            "Best regards,\n"
            "Invoice Manager",
            username=instance.username,
        )
        send_mail(
            subject,
            content,
            from_email=settings.EMAIL_SENDER,
            recipient_list=[instance.email],
        )


@receiver(post_delete, sender=User)
def send_goodbye_email(sender, instance: User, **kwargs):
    if instance.email:
        subject = _("Goodbye in Invoice Manager")
        content = _(
            "Thank you for using our Invoice Manager\n"
            "We hope you will come back to us again: {username}\n"
            "Best regards,\n"
            "Invoice Manager",
            username=instance.username,
        )
        send_mail(
            subject,
            content,
            from_email=settings.EMAIL_SENDER,
            recipient_list=[instance.email],
        )
