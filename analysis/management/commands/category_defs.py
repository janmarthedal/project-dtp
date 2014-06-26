from django.core.management.base import BaseCommand
import analysis.helpers
from analysis.models import DecorateCategory
from tags.models import Category

class Command(BaseCommand):
    help = 'Category definitions'

    def handle(self, *args, **options):
        DecorateCategory.objects.all().delete()
        total_category_count = 0
        nontrivial_category_count = 0
        for cat in analysis.helpers.queryset_generator(Category.objects.all()):
            total_category_count += 1
            dc = DecorateCategory(category=cat)
            analysis.helpers.decorate_category(dc)
            dc.save()
            if dc.refer_count > 0 or dc.max_points is not None:
                nontrivial_category_count += 1
        for entry in DecorateCategory.objects.order_by('score').all():
            self.stdout.write('{}  {}  {}  [{}]'.format(entry.refer_count, entry.max_points,
                                                        entry.score, ','.join(map(str, entry.category.get_tag_list()))))

        self.stdout.write('Processed {} categories, {} non-trivial'.format(total_category_count, nontrivial_category_count))
