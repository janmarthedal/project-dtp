from django.db import models
from tags.helpers import normalize_tag


class TagManager(models.Manager):

    def fetch(self, name):
        normalized = normalize_tag(name)
        tag, created = self.get_or_create(name=name,
                                          defaults={'normalized':normalized})
        return tag


class Tag(models.Model):
    
    class Meta:
        db_table = 'tags'
    
    objects = TagManager()

    name       = models.CharField(max_length=255, db_index=True, unique=True)
    normalized = models.CharField(max_length=255, db_index=True, unique=False)
    
    def __unicode__(self):
        return self.name


class Concept(models.Model):
    
    class Meta:
        db_table = 'concepts'
    
    primary     = models.ForeignKey(Tag)
    secondaries = models.ManyToManyField(Tag, related_name='+')

