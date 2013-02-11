from django.db import models
from django.conf import settings
from django.utils import timezone
from items.models import FinalItem
from refs.models import RefNode

class SourceValidation(models.Model):
    class Meta:
        db_table = 'source_validation'
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+')
    created_at = models.DateTimeField(default=timezone.now)
    item       = models.ForeignKey(FinalItem)
    source     = models.ForeignKey(RefNode)
    location   = models.CharField(max_length=64, null=True, blank=True)

