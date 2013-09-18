import time
from django.core.management.base import BaseCommand, CommandError
from analysis.models import ItemDependency, TagCount, ItemTag
from items.models import FinalItem, ItemTagCategory
from items.helpers import BodyScanner
from tags.models import Tag, Category

def queryset_generator(queryset):
    items = queryset.order_by('pk')[:100]
    while items:
        latest_pk = items[len(items) - 1].pk
        for item in items:
            yield item
        items = queryset.filter(pk__gt=latest_pk).order_by('pk')[:100]

def add_final_item_dependencies(from_item):
    bs = BodyScanner(from_item.body)
    try:
        to_item_list = [FinalItem.objects.get(final_id=itemref_id) for itemref_id in bs.getItemRefSet()] 
    except ValueError:
        raise CommandError("add_final_item_dependencies: illegal item name '%s'" % itemref_id)
    except FinalItem.DoesNotExist:
        raise CommandError("add_final_item_dependencies: non-existent item '%s'" % str(itemref_id))
    ItemDependency.objects.filter(from_item=from_item).delete()
    ItemDependency.objects.bulk_create([ItemDependency(from_item=from_item, to_item=to_item)
                                        for to_item in to_item_list])

def check_final_item_tag_categories(fitem):
    bs = BodyScanner(fitem.body)

    tags_in_item = set([Tag.objects.fetch(tag_name) for tag_name in bs.getConceptSet()])
    tags_in_db = set([itc.tag for itc in fitem.itemtagcategory_set.all()])
    tags_to_remove = tags_in_db - tags_in_item
    tags_to_add = tags_in_item - tags_in_db

    for tag in tags_to_remove:
        ItemTagCategory.objects.filter(item=fitem, tag=tag).delete()

    for tag in tags_to_add:
        category = Category.objects.default_category_for_tag(tag)
        ItemTagCategory.objects.create(item=fitem, tag=tag, category=category)

    return len(tags_to_add), len(tags_to_remove)

class Command(BaseCommand):
    help = 'Builds (redundant) analysis information'

    def handle(self, *args, **options):
        self._rebuild_dependencies()
        self._check_item_tag_categories()
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

    def _check_item_tag_categories(self):
        self.stdout.write('Check item tag categories')
        t = time.clock()
        item_count = 0
        added = 0
        removed = 0
        for fitem in queryset_generator(FinalItem.objects.filter(status='F')):
            changes = check_final_item_tag_categories(fitem)
            added += changes[0]
            removed += changes[1]
            item_count += 1
        t = time.clock() - t
        self.stdout.write('  Processed %d final items' % item_count)
        self.stdout.write('  Added %d item tag categories' % added)
        self.stdout.write('  Removed %d item tag categories' % removed)
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
