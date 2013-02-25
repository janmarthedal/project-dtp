from django.db import models
from django.conf import settings
from django.utils import timezone

class RefAuthor(models.Model):
    class Meta:
        db_table = 'ref_author'
    name = models.CharField(max_length=64)
    def __unicode__(self):
        return self.name

class RefNode(models.Model):
    class Meta:
        db_table = 'ref_node'
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+')
    created_at = models.DateTimeField(default=timezone.now)
    authors    = models.ManyToManyField(RefAuthor, blank=True)
    title      = models.CharField(max_length=256, null=True, blank=True)
    isbn10     = models.CharField(max_length=10, null=True, blank=True)
    isbn13     = models.CharField(max_length=13, null=True, blank=True)
    publisher  = models.CharField(max_length=64, null=True, blank=True)
    series     = models.CharField(max_length=64, null=True, blank=True)
    edition    = models.CharField(max_length=16, null=True, blank=True)
    volume     = models.CharField(max_length=16, null=True, blank=True)
    year       = models.IntegerField(null=True, blank=True)
    extra      = models.CharField(max_length=256, null=True, blank=True)

