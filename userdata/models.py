from django.conf import settings
from django.db import models

from userdata.permissions import DEFAULT_PERMS


class UserDataManager(models.Manager):
    def new_user(self, user):
        return self.create(user=user, perms=','.join(DEFAULT_PERMS))


class UserData(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, models.CASCADE, primary_key=True)
    perms = models.CharField(max_length=128, default='', blank=True)
    objects = UserDataManager()

    class Meta:
        db_table = 'userdata'
