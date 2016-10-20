from django.conf import settings
from django.db import models

from mathitems.models import MathItem

class Source(models.Model):
    SOURCE_TYPE_CHOICES = (
        ('isbn10', 'ISBN-10'),
        ('isbn13', 'ISBN-13'),
    )
    source_type = models.CharField(max_length=8, choices=SOURCE_TYPE_CHOICES)
    source_value = models.CharField(max_length=255)
    metadata = models.TextField(blank=True)

    def __str__(self):
        return 'ISBN {}'.format(self.source_value)

class ItemValidation(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True)
    item = models.ForeignKey(MathItem)
    source = models.ForeignKey(Source)
    location = models.CharField(max_length=255)
