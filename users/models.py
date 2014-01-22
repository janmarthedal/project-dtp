from django.db import models
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

class UserManager(BaseUserManager):

    def create_user(self, fullname=None, email=None, **kwargs):
        user = self.model(name=fullname, email=UserManager.normalize_email(email))
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(max_length=255, null=True)
    name = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'id'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        return self.name or 'User %d' % self.id

    def get_short_name(self):
        return self.id

    def __unicode__(self):
        return self.name

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin
