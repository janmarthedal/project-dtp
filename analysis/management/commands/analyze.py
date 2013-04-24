import time
from django.core.management.base import BaseCommand, CommandError
from analysis.models import ItemDependency, ItemConceptReference, Concept, ConceptDefinition, TagCount
from items.models import FinalItem
from items.helpers import BodyScanner
from tags.models import Tag

def queryset_generator(queryset):
    items = queryset.order_by('pk')[:100]
    while items:
        latest_pk = items[len(items) - 1].pk
        for item in items:
            yield item
        items = queryset.filter(pk__gt=latest_pk).order_by('pk')[:100]

def add_final_item_dependencies(fitem):
    bs = BodyScanner(fitem.body)

    ItemDependency.objects.filter(from_item=fitem).delete()
    for itemref_id in bs.getItemRefList():
        try:
            itemref_item = FinalItem.objects.get(final_id=itemref_id)
            itemdep = ItemDependency(from_item=fitem, to_item=itemref_item)
            itemdep.save()
        except ValueError:
            raise CommandError("add_final_item_dependencies: illegal item name '%s'" % itemref_id)
        except FinalItem.DoesNotExist:
            raise CommandError("add_final_item_dependencies: non-existent item '%s'" % str(itemref_id))

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

class Command(BaseCommand):
    help = 'Builds (redundant) analysis information'

    def handle(self, *args, **options):
        self._rebuild_dependencies()
        self._build_concept_definitions()
        self._build_tag_counts()

    def _rebuild_dependencies(self):
        self.stdout.write('Rebuild dependencies')
        t = time.clock()
        item_count = 0
        for fitem in queryset_generator(FinalItem.objects.filter(status='F')):
            add_final_item_dependencies(fitem)
            item_count += 1
        t = time.clock() - t
        self.stdout.write('  Processed %d published items' % item_count)
        self.stdout.write('  A total of %d item dependencies and %d concept references'
                          % (ItemDependency.objects.count(), ItemConceptReference.objects.count()))
        self.stdout.write('  Took %g seconds' % t)

    def _build_concept_definitions(self):
        self.stdout.write('Build concept definitions')
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
        self.stdout.write('  Processed %d concepts' % Concept.objects.count())
        self.stdout.write('  Created %d concept definition links' % ConceptDefinition.objects.count())
        self.stdout.write('  Took %g seconds' % t)

    def _build_tag_counts(self):
        self.stdout.write('Build tag count')
        t = time.clock()
        TagCount.objects.all().delete()
        for tag in queryset_generator(Tag.objects):
            count = FinalItem.objects.filter(status='F', finalitemtag__tag=tag).count()
            tag_count = TagCount(tag=tag, count=count)
            tag_count.save()
        t = time.clock() - t
        self.stdout.write('  Processed %d tags' % TagCount.objects.count())
        self.stdout.write('  Took %g seconds' % t)
