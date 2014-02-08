import uuid
from django.conf import settings
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from drafts.models import DraftItem
from items.models import FinalItem

class UserManager(BaseUserManager):

    def create_user(self, fullname=None, email=None, **kwargs):
        user = self.model(name=fullname, email=UserManager.normalize_email(email))
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(max_length=255, null=True)
    name = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    points = models.FloatField(default=0, null=False)

    objects = UserManager()

    USERNAME_FIELD = 'id'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        return self.name or 'User {}'.format(self.id)

    def get_short_name(self):
        return self.id

    def __unicode__(self):
        return self.name

    def has_perm(self, perm, obj=None):
        if isinstance(obj, DraftItem):
            if perm == 'view':
                return obj.status == 'R' or (obj.status == 'D' and obj.created_by == self)
            if perm in ['add_source', 'edit', 'delete', 'to_review']:
                return obj.status == 'D' and obj.created_by == self
            if perm == 'to_draft':
                return obj.status == 'R' and obj.created_by == self
            if perm == 'to_final':
                return obj.status in ['D', 'R'] and obj.created_by == self
        elif isinstance(obj, FinalItem):
            if perm == 'add_proof':
                return obj.status == 'F' and obj.itemtype == 'T'
            if perm in ['add_source', 'add_to_doc']:
                return obj.status == 'F'
            if perm == 'change_cats':
                return obj.status == 'F' and self.point >= 100
            if perm == 'delete':
                return self.is_admin
        return False


class InvitationManager(models.Manager):

    def make_invitation(self, invited_by=None, target_email=None, target_name=None):
        invite = self.model(invited_by=invited_by, token=uuid.uuid4().hex,
                            target_email=target_email, target_name=target_name)
        invite.save()
        return invite

class Invitations(models.Model):
    token = models.CharField(max_length=32, db_index=True, null=False)
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+', db_index=False, null=True)
    invited_at = models.DateTimeField(default=timezone.now)
    target_email = models.EmailField(max_length=255, null=True)
    target_name = models.CharField(max_length=255, null=True)
    objects = InvitationManager()

    def send(self):
        if not self.target_email:
            raise ValueError('No email address present')
        email = render_to_string('email/beta_invite.txt',
                                 {'site_url': settings.SITE_URL, 'token': self.token,
                                  'name': self.target_name})
        [subject, message] = email.split('\n', 1)
        send_mail(subject, message, 'admin@teoremer.com', [self.target_email])

    def __unicode__(self):
        return u'{} for {} <{}>'.format(self.token, self.target_name, self.target_email)
