from django.core.management.base import BaseCommand
from django.db.models import Sum
from analysis.helpers import queryset_generator
from items.models import ItemValidation

class Command(BaseCommand):
    help = 'Recomputes all item/validation points'

    def handle(self, *args, **options):
        # TODO: Can we do better?
        for iv in queryset_generator(ItemValidation.objects.annotate(sub_points=Sum('useritemvalidation__value'))):
            iv.points = iv.sub_points or 0
            iv.save()
