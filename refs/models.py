from django.db import models
from django.conf import settings
from django.utils import timezone

class RefField(models.Model):
    class Meta:
        db_table = 'ref_field'
    name = models.CharField(max_length=32)

class RefAttribute(models.Model):
    class Meta:
        db_table = 'ref_attribute'
    field = models.ForeignKey(RefField)
    value = models.CharField(max_length=128)

class RefNode(models.Model):
    class Meta:
        db_table = 'ref_node'
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+')
    created_at = models.DateTimeField(default=timezone.now)
    attributes = models.ManyToManyField(RefAttribute)

