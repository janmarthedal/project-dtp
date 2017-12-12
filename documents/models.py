from django.conf import settings
from django.db import models

from mathitems.models import MathItem


class Document(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=64)

    class Meta:
        db_table = 'documents'

    def __str__(self):
        return '{} (Document {})'.format(self.name, self.pk)


class DocumentItem(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    item = models.ForeignKey(MathItem, on_delete=models.CASCADE)
    order = models.FloatField()

    class Meta:
        db_table = 'document_items'
        unique_together = ('document', 'order')

    def __str__(self):
        return '{} in {} at {}'.format(self.item, self.document, self.order)
