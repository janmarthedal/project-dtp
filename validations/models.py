import json
import re
from django.conf import settings
from django.core.exceptions import ValidationError
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

    class Meta:
        db_table = 'sources'

    def __str__(self):
        return 'ISBN {}'.format(self.source_value)

    def metadata_object(self):
        return json.loads(self.metadata)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        source_type = self.source_type
        source_value = self.source_value
        if source_type in ['isbn10', 'isbn13']:
            source_value = re.sub(r'[ -]', '', source_value.upper())
            self.source_value = source_value
        if source_type == 'isbn10':
            if not re.match(r'^[0-9]{9}[0-9X]$', source_value):
                raise ValidationError('Illegal ISBN-10 format')
            digits = [10 if c == 'X' else ord(c)-ord('0') for c in source_value]
            if sum((10-n)*v for n, v in enumerate(digits)) % 11:
                raise ValidationError('Illegal ISBN-10 checksum')
        elif source_type == 'isbn13':
            if not re.match(r'^[0-9]{12}[0-9X]$', source_value):
                raise ValidationError('Illegal ISBN-13 format')
            digits = [ord(c)-ord('0') for c in source_value]
            if sum((3 if n % 2 else 1) * v for n, v in enumerate(digits)) % 10:
                raise ValidationError('Illegal ISBN-13 checksum')


class ItemValidation(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True)
    item = models.ForeignKey(MathItem)
    source = models.ForeignKey(Source)
    location = models.CharField(max_length=255)

    class Meta:
        db_table = 'item_validations'
