from django.db import models
from django.conf import settings
from django.utils import timezone
from items.models import Item
from refs.models import RefNode, RefAttribute

class SourceValidation(models.Model):
    class Meta:
        db_table = 'source_validation'
    item       = models.ForeignKey(Item)
    source     = models.ForeignKey(RefNode)
    location   = models.ManyToManyField(RefAttribute)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+')
    created_at = models.DateTimeField(default=timezone.now)

