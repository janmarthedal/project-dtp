from django.db import models
from django.utils import timezone
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)


class MyUserManager(BaseUserManager):
    def create_user(self, name, email=None, password=None):
        if not name:
            raise ValueError('Users must have a name')
        user = self.model(name=name)
        if email:
            user.email = MyUserManager.normalize_email(email)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, id, name, password, email=None):
        if not name:
            raise ValueError('Users must have a name')
        user = self.model(id=id, name=name)
        if email:
            user.email = MyUserManager.normalize_email(email)
        user.set_password(password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    email = models.EmailField(verbose_name='email address', max_length=255, db_index=True, null=True, blank=True)
    name = models.CharField(verbose_name='full name', max_length=255)
    created_at = models.DateTimeField(verbose_name='created at', default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'id'
    REQUIRED_FIELDS = ['name']

    def get_full_name(self):
        # The user is identified by their email address
        return self.name

    def get_short_name(self):
        # The user is identified by their email address
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

