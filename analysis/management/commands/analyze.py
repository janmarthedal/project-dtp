import time
from django.core.management.base import BaseCommand, CommandError
from analysis.models import ItemDependency, TagCount, ItemTag
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

class Command(BaseCommand):
    help = 'Builds (redundant) analysis information'

    def handle(self, *args, **options):
        self._rebuild_dependencies()
        self._build_item_tags()
        self._build_tag_counts()

    def _rebuild_dependencies(self):
        self.stdout.write('Rebuild dependencies')
        t = time.clock()
        item_count = 0
        for fitem in queryset_generator(FinalItem.objects.filter(status='F')):
            add_final_item_dependencies(fitem)
            item_count += 1
        t = time.clock() - t
        self.stdout.write('  Processed %d final items' % item_count)
        self.stdout.write('  A total of %d item dependencies' % ItemDependency.objects.count())
        self.stdout.write('  Took %g seconds' % t)

    def _build_item_tags(self):
        self.stdout.write('Build item tags')
        t = time.clock()
        item_count = 0
        tag_count = 0
        for item in queryset_generator(FinalItem.objects.filter(status='F')):
            tags = set([tag for itemtag in item.finalitemcategory_set.all()
                            for tag in itemtag.category.get_tag_list()])
            for tag in tags:
                it = ItemTag(item=item, tag=tag)
                it.save()
                tag_count += 1
            item_count += 1
        t = time.clock() - t
        self.stdout.write('  Processed %d final items' % item_count)
        self.stdout.write('  A total of %d item tags' % tag_count)
        self.stdout.write('  Took %g seconds' % t)

    def _build_tag_counts(self):
        self.stdout.write('Build tag count')
        t = time.clock()
        TagCount.objects.all().delete()
        for tag in queryset_generator(Tag.objects):
            count = ItemTag.objects.filter(tag=tag).count()
            tag_count = TagCount(tag=tag, count=count)
            tag_count.save()
        t = time.clock() - t
        self.stdout.write('  Processed %d tags' % TagCount.objects.count())
        self.stdout.write('  Took %g seconds' % t)
