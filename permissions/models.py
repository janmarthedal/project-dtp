from django.conf import settings
from django.db import models

class Permission(models.Model):
    name = models.CharField(max_length=1, unique=True)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)

    def __str__(self):
        return self.name
