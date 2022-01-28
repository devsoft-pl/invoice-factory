from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.core.mail import send_mail


@receiver(post_save, sender=User)
def send_welcome_email(sender, instance: User, created=False, **kwargs):
    if created and instance.email:
        send_mail('Welcome in Invoice Manager', f'Thanks for your registration. Your account details: \n '
                                                f'Login: {instance.username} \n'
                                                f'Best regards,\n'
                                                f'Invoice Manager',
                  from_email='wioletta.wajda82@gmail.com',
                  recipient_list=[instance.email])



