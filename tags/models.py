from django.db import models
from tags.helpers import normalize_tag

import logging
logger = logging.getLogger(__name__)


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


class ConceptManager(models.Manager):
    
    def fetch(self, primary, secondaries):
        primary_tag = Tag.objects.fetch(primary)
        query = Concept.objects.annotate(models.Count('secondaries')).filter(primary=primary_tag, secondaries__count=len(secondaries))
        secondary_tags = map(Tag.objects.fetch, secondaries)
        for secondary_tag in secondary_tags:
            query.filter(secondaries=secondary_tag)
        concepts = query.all()
        if not concepts:
            concept = Concept(primary=primary_tag)
            concept.save()
            if secondary_tags:
                concept.secondaries = secondary_tags
                concept.save()
            return concept
        if len(concepts) > 1:
            logger.warn('Identical concepts: ' + str([c.id for c in concepts]))
        return concepts[0]


class Concept(models.Model):
    
    class Meta:
        db_table = 'concepts'

    objects = ConceptManager()
    
    primary     = models.ForeignKey(Tag)
    secondaries = models.ManyToManyField(Tag, related_name='+')

