from django.db import models

from mathitems.models import MathItem

class Source(models.Model):
    SOURCE_TYPE_CHOICES = (
        ('isbn10', 'ISBN-10'),
        ('isbn13', 'ISBN-13'),
    )
    source_type = models.CharField(max_length=8, choices=SOURCE_TYPE_CHOICES)
    source_value = models.CharField(max_length=255)

class ItemValidation(models.Model):
    item = models.ForeignKey(MathItem)
    source = models.ForeignKey(Source)
    location = models.CharField(max_length=255)
