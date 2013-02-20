from django.db import models
from tags.models import Tag
from items.models import FinalItem, final_name_to_id
from items.helpers import BodyScanner

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
    primary     = models.ForeignKey(Tag, related_name='+')
    secondaries = models.ManyToManyField(Tag, related_name='+')


class ItemDependency(models.Model):
    class Meta:
        db_table = 'item_deps'
        unique_together = ('from_item', 'to_item')
    from_item = models.ForeignKey(FinalItem, related_name='+')
    to_item   = models.ForeignKey(FinalItem, related_name='+')


class ItemConceptReference(models.Model):
    class Meta:
        db_table = 'item_concept_refs'
        unique_together = ('item', 'concept')
    item    = models.ForeignKey(FinalItem, related_name='+')
    concept = models.ForeignKey(Concept, related_name='+')


def add_final_item_dependencies(fitem):
    bs = BodyScanner(fitem.body)

    for itemref_name in bs.getItemRefList():
        try:
            itemref_id = final_name_to_id(itemref_name)
            itemref_item = FinalItem.objects.get(pk=itemref_id)
            itemdep = ItemDependency(from_item=fitem, to_item=itemref_item)
            itemdep.save()
        except ValueError:
            logger.error("set_dependencies: illegal item name '%s'" % itemref_name)
        except FinalItem.DoesNotExist:
            logger.error("set_dependencies: non-existent item '%s'" % str(itemref_id))
    
    for concept_struct in bs.getConceptList():
        concept = Concept.objects.fetch(*concept_struct)
        conceptref = ItemConceptReference(item=fitem, concept=concept)
        conceptref.save()


def recalc_all():
    ItemDependency.objects.all().delete()
    ItemConceptReference.objects.all().delete()
    fitems = FinalItem.objects.filter(status='F').all()
    for fitem in fitems:
        add_final_item_dependencies(fitem)
    c = { 'public_item_count':  len(fitems),
          'concept_references': ItemConceptReference.objects.count(),
          'item_dependencies':  ItemDependency.objects.count() }
    return c
