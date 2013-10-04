import string
from django.conf import settings
from django.db import models, IntegrityError
from django.utils import timezone
from django.utils.crypto import get_random_string
from tags.models import Category

PUBLIC_ID_CHARS = string.digits
PUBLIC_ID_MIN_LENGTH = 4
PUBLIC_ID_MAX_LENGTH = 10

class MediaEntryManager(models.Manager):

    def add_entry(self, user):
        entry = MediaEntry(created_by=user)
        for length in range(PUBLIC_ID_MIN_LENGTH, PUBLIC_ID_MAX_LENGTH):
            entry.public_id = 'M' + get_random_string(length, PUBLIC_ID_CHARS)
            try:
                entry.save()
                return entry
            except IntegrityError:
                pass
        raise Exception('MediaEntryManager.add_entry')

class MediaEntry(models.Model):
    class Meta:
        db_table = 'media_entry'
    objects = MediaEntryManager()
    public_id  = models.CharField(max_length=10, unique=True, db_index=True, null=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+', db_index=False)
    created_at = models.DateTimeField(default=timezone.now)
    categories = models.ManyToManyField(Category)

class MediaItem(models.Model):
    class Meta:
        db_table = 'media_item'
    TYPE_CHOICES = (
        ('O', 'original'),
        ('T', 'thumbnail'),
        ('E', 'extra'),
    )
    entry    = models.ForeignKey(MediaEntry, db_index=True)
    path     = models.CharField(max_length=255, null=False)
    format   = models.CharField(max_length=32, null=False)
    width    = models.IntegerField(null=False)
    height   = models.IntegerField(null=False)
    itemtype = models.CharField(max_length=1, choices=TYPE_CHOICES)
