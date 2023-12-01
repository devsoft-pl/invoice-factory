from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import EmailMessage
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("Email"), unique=True)
    first_name = models.CharField(_("First name"), max_length=75, null=True)
    last_name = models.CharField(_("Last name"), max_length=75, null=True)
    is_staff = models.BooleanField(
        _("Staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("Active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. Unselect this instead of deleting accounts."
        ),
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self) -> str:
        return self.email

    def send_email(self, subject, content, files=None):
        if not self.email:
            return

        email = EmailMessage(
            subject,
            content,
            settings.EMAIL_SENDER,
            [self.email],
        )

        if files:
            for data in files:
                email.attach(data["name"], data["content"])

        return email.send()


@receiver(post_save, sender=User)
def send_welcome_email(sender, instance: User, created=False, **kwargs):
    if created:
        subject = _(f"Welcome in Factorka")
        content = _(
            "Thanks for your registration in Factorka. Your account details:\n"
            "Login: {email}\n"
            "Best regards,\n"
            "Factorka",
        ).format(email=instance.email)
        User().send_email(subject, content)
