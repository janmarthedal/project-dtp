import time
from django.core.management.base import BaseCommand
from analysis.helpers import queryset_generator
from analysis.models import ItemDependency, ItemTag, add_final_item_dependencies
from items.models import FinalItem, check_final_item_tag_categories

class Command(BaseCommand):
    help = 'Builds (redundant) analysis information'

    def handle(self, *args, **options):
        self._rebuild_dependencies()
        self._check_item_tag_categories()
        self._build_item_tags()

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
