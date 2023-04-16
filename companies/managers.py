from django.db import models


class MyClientsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(is_my_company=True)
