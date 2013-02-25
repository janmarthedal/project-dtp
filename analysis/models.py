import time
from django.db import models
from tags.models import Tag
from items.models import FinalItem, final_name_to_id
from items.helpers import BodyScanner

import logging
logger = logging.getLogger(__name__)


def queryset_generator(queryset):
    items = queryset.order_by('pk')[:100]
    while items:
        latest_pk = items[len(items) - 1].pk
        for item in items:
            yield item
        items = queryset.filter(pk__gt=latest_pk).order_by('pk')[:100]


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


def add_final_item_dependencies(fitem):
    bs = BodyScanner(fitem.body)

    ItemDependency.objects.filter(from_item=fitem).delete()
    for itemref_name in bs.getItemRefList():
        try:
            itemref_id = final_name_to_id(itemref_name)
            itemref_item = FinalItem.objects.get(pk=itemref_id)
            itemdep = ItemDependency(from_item=fitem, to_item=itemref_item)
            itemdep.save()
        except ValueError:
            logger.error("add_final_item_dependencies: illegal item name '%s'" % itemref_name)
        except FinalItem.DoesNotExist:
            logger.error("add_final_item_dependencies: non-existent item '%s'" % str(itemref_id))

    ItemConceptReference.objects.filter(item=fitem).delete()    
    for concept_struct in bs.getConceptList():
        concept = Concept.objects.fetch(*concept_struct)
        conceptref = ItemConceptReference(item=fitem, concept=concept)
        conceptref.save()


def set_concept_counters():
    for concept in queryset_generator(Concept.objects):
        concept.refs_to_this = concept.concept_refs.count()
        concept.defs_for_this = concept.concept_defs.count()
        concept.save()


def build_concept_definitions():
    t = time.clock()
    ConceptDefinition.objects.all().delete()
    for concept in queryset_generator(Concept.objects):
        query = FinalItem.objects.filter(itemtype='D', status='F', finalitemtag__tag=concept.primary, finalitemtag__primary=True)
        for secondary_tag in concept.secondaries.all():
            query = query.filter(finalitemtag__tag=secondary_tag)
        definition_list = query.all()
        for item in definition_list:
            cd = ConceptDefinition(concept=concept, item=item)
            cd.save()
    set_concept_counters()
    t = time.clock() - t
    c = { 'concept_count':            Concept.objects.count(),
          'concept_definition_count': ConceptDefinition.objects.count(), 
          'time':                     t }
    return c


def rebuild_dependencies():
    t = time.clock()
    item_count = 0
    for fitem in queryset_generator(FinalItem.objects.filter(status='F')):
        add_final_item_dependencies(fitem)
        item_count += 1
    t = time.clock() - t
    c = { 'public_item_count':  item_count,
          'concept_references': ItemConceptReference.objects.count(),
          'item_dependencies':  ItemDependency.objects.count(),
          'time':               t }
    return c


