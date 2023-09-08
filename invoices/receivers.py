from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils.text import format_lazy as _

from users.models import User


@receiver(post_save, sender=User)
def send_welcome_email(sender, instance: User, created=False, **kwargs):
    if created:
        subject = _(f"Welcome in Factorka")
        content = _(
            "Thanks for your registration in Factorka. Your account details:\n"
            "Login: Your email\n"
            "Best regards,\n"
            "Factorka",
            username=instance.email,
        )
        send_mail(
            subject,
            content,
            from_email=settings.EMAIL_SENDER,
            recipient_list=[instance.email],
        )


@receiver(post_delete, sender=User)
def send_goodbye_email(sender, instance: User, **kwargs):
    subject = _("Goodbye in Factorka")
    content = _(
        "Thank you for using our Factorka\n"
        "We hope you will come back to us again\n"
        "Best regards,\n"
        "Factorka",
        username=instance.email,
    )
    send_mail(
        subject,
        content,
        from_email=settings.EMAIL_SENDER,
        recipient_list=[instance.email],
    )
