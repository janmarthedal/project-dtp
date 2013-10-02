from django.conf import settings
from django.db import models
from django.utils import timezone
from tags.models import Category

class MediaEntry(models.Model):
    class Meta:
        db_table = 'media_entry'
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+', db_index=False)
    created_at = models.DateTimeField(default=timezone.now)
    categories = models.ManyToManyField(Category)

# image/gif
# image/jpeg
# image/png
# image/svg+xml

class MediaItem(models.Model):
    class Meta:
        db_table = 'media_item'
    entry  = models.ForeignKey(MediaEntry)
    path   = models.CharField(max_length=255)
    format = models.CharField(max_length=32, null=False)
    width  = models.IntegerField(null=False)
    height = models.IntegerField(null=False)
