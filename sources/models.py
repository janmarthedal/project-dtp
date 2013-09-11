from django.db import models
from django.conf import settings
from django.utils import timezone
from items.models import FinalItem

class RefAuthor(models.Model):
    class Meta:
        db_table = 'ref_author'
    name = models.CharField(max_length=255, unique=True)
    def __unicode__(self):
        return self.name

class RefNode(models.Model):
    class Meta:
        db_table = 'ref_node'
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+', db_index=False)
    created_at = models.DateTimeField(default=timezone.now, db_index=False)
    sourcetype = models.CharField(max_length=20, null=False)
    authors    = models.ManyToManyField(RefAuthor, related_name='auth+')
    editors    = models.ManyToManyField(RefAuthor, related_name='ed+')
    title      = models.CharField(max_length=255, db_index=True, null=True)
    publisher  = models.CharField(max_length=255, null=True)
    year       = models.CharField(max_length=255, null=True)
    volume     = models.CharField(max_length=255, null=True)
    number     = models.CharField(max_length=255, null=True)
    series     = models.CharField(max_length=255, null=True)
    address    = models.CharField(max_length=255, null=True)
    edition    = models.CharField(max_length=255, null=True)
    month      = models.CharField(max_length=255, null=True)
    journal    = models.CharField(max_length=255, null=True)
    pages      = models.CharField(max_length=255, null=True)
    isbn10     = models.CharField(max_length=255, null=True)
    isbn13     = models.CharField(max_length=255, null=True)
    note       = models.CharField(max_length=255, null=True)
    STRING_FIELDS = ['title', 'publisher', 'year', 'volume', 'number', 'series', 'address', 'edition',
                    'month', 'journal', 'pages', 'isbn10', 'isbn13', 'note']
    def __unicode__(self):
        if self.pk:
            return 'Source %d' % self.pk
        return 'New source'
    def json_serializable(self):
        data = { 'id': self.pk, 'type': self.sourcetype }
        for key in RefNode.STRING_FIELDS:
            if self.__dict__[key]:
                data[key] = self.__dict__[key]
        names = [a.name for a in self.authors.all()]
        if names: data['author'] = names
        names = [a.name for a in self.editors.all()]
        if names: data['editor'] = names 
        return data

class SourceValidation(models.Model):
    class Meta:
        db_table = 'source_validation'
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+')
    created_at = models.DateTimeField(default=timezone.now, db_index=False)
    item       = models.ForeignKey(FinalItem)
    source     = models.ForeignKey(RefNode)
    location   = models.CharField(max_length=255, null=True)
