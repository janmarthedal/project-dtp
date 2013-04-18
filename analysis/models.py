from django.db import models
from tags.models import Tag
from items.models import FinalItem

import logging
logger = logging.getLogger(__name__)


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
    primary       = models.ForeignKey(Tag, related_name='+', db_index=True)
    secondaries   = models.ManyToManyField(Tag, related_name='+')
    refs_to_this  = models.IntegerField(null=True)
    defs_for_this = models.IntegerField(null=True)
    def __unicode__(self):
        return self.primary.name


class ItemDependency(models.Model):
    class Meta:
        db_table = 'item_deps'
        unique_together = ('from_item', 'to_item')
    from_item = models.ForeignKey(FinalItem, related_name='+', db_index=True)
    to_item   = models.ForeignKey(FinalItem, related_name='+')


class ItemConceptReference(models.Model):
    class Meta:
        db_table = 'item_concept_refs'
        unique_together = ('item', 'concept')
    item    = models.ForeignKey(FinalItem, related_name='+', db_index=True)
    concept = models.ForeignKey(Concept, related_name='concept_refs')


class ConceptDefinition(models.Model):
    class Meta:
        db_table = 'concept_definition'
        unique_together = ('item', 'concept')
    concept = models.ForeignKey(Concept, related_name='concept_defs')
    item    = models.ForeignKey(FinalItem, related_name='+')

