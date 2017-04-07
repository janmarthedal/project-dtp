from django.conf import settings
from django.db import models


class UserData(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, models.CASCADE, primary_key=True)
    perms = models.CharField(max_length=128, blank=True)  # draft,keyword,publish,validation

    class Meta:
        db_table = 'userdata'
