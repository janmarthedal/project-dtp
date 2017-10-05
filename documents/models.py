from django.conf import settings
from django.db import models

from mathitems.models import MathItem


class Document(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=64)

    class Meta:
        db_table = 'documents'


class DocumentItem(models.Model):
    parent = models.ForeignKey(Document, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    item = models.ForeignKey(MathItem, on_delete=models.CASCADE)
    order = models.FloatField()

    class Meta:
        db_table = 'document_items'
