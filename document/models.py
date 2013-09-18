from django.conf import settings
from django.db import models
from django.utils import timezone
from items.models import FinalItem

class Document(models.Model):
    class Meta:
        db_table = 'documents'
    created_by  = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+', db_index=True)
    created_at  = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(default=timezone.now)
    title       = models.CharField(max_length=255, null=True)
    def __unicode__(self):
        return "%d. %s" % (self.id, self.title)

class DocumentItem(models.Model):
    class Meta:
        db_table = 'document_item'
        unique_together = ('document', 'item', 'order')
    document = models.ForeignKey(Document, db_index=True)
    item     = models.ForeignKey(FinalItem, db_index=False)
    order    = models.FloatField(null=False)
