from django.core.management.base import BaseCommand
from django.db.models import Max
from analysis.helpers import queryset_generator
from analysis.models import CategoryDefinitionUsage
from items.models import FinalItem
from tags.models import Category

class Command(BaseCommand):
    help = 'Category definitions'

    def handle(self, *args, **options):
        CategoryDefinitionUsage.objects.all().delete()
        total_category_count = 0
        nontrivial_category_count = 0
        for cat in queryset_generator(Category.objects.all()):
            total_category_count += 1
            ref_count=FinalItem.objects.filter(status='F', itemtagcategory__category=cat).count()
            max_points=FinalItem.objects.filter(status='F', itemtype='D', finalitemcategory__primary=True,
                                                finalitemcategory__category=cat).aggregate(Max('points'))['points__max']
            if ref_count or max_points is not None:
                CategoryDefinitionUsage.objects.create(category=cat, refer_count=ref_count, max_points=max_points)
                nontrivial_category_count += 1
        for entry in CategoryDefinitionUsage.objects.order_by('score').all():
            self.stdout.write('{}  {}  {}  [{}]'.format(entry.refer_count, entry.max_points,
                                                        entry.score, ','.join(map(str, entry.category.get_tag_list()))))

        self.stdout.write('Processed {} categories, {} non-trivial'.format(total_category_count, nontrivial_category_count))
