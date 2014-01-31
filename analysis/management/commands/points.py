from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.models import Sum
from analysis.helpers import queryset_generator
from items.models import FinalItem, ItemValidation

class Command(BaseCommand):
    help = 'Recomputes all item/validation points'

    def handle(self, *args, **options):
        total = 0
        changed = 0
        for item in queryset_generator(ItemValidation.objects.annotate(validation_points=Sum('useritemvalidation__value'))):
            total += 1
            new_points = item.validation_points or 0
            if new_points != item.points:
                changed += 1
                item.points = new_points
                item.save()
        self.stdout.write('{} validations, {} points changed'.format(total, changed))

        total = 0
        changed = 0
        for item in queryset_generator(FinalItem.objects.filter(status='F', itemtype='P')):
            total += 1
            sum_aggregate = ItemValidation.objects.filter(item=item, points__gt=0).aggregate(Sum('points'))
            new_points = 1 + (sum_aggregate['points__sum'] or 0)
            if new_points != item.points:
                changed += 1
                item.points = new_points
                item.save()
        self.stdout.write('{} proofs, {} points changed'.format(total, changed))

        total = 0
        changed = 0
        for item in queryset_generator(FinalItem.objects.filter(status='F', itemtype='T')):
            total += 1
            new_points = 1
            sum_aggregate = ItemValidation.objects.filter(item=item, points__gt=0).aggregate(Sum('points'))
            new_points += sum_aggregate['points__sum'] or 0
            sum_aggregate = FinalItem.objects.filter(parent=item, status='F', itemtype='P', points__gt=0).aggregate(Sum('points'))
            new_points += sum_aggregate['points__sum'] or 0
            if new_points != item.points:
                changed += 1
                item.points = new_points
                item.save()
        self.stdout.write('{} theorems, {} points changed'.format(total, changed))

        total = 0
        changed = 0
        for item in queryset_generator(FinalItem.objects.filter(status='F', itemtype='D')):
            total += 1
            sum_aggregate = ItemValidation.objects.filter(item=item, points__gt=0).aggregate(Sum('points'))
            new_points = 1 + (sum_aggregate['points__sum'] or 0)
            if new_points != item.points:
                changed += 1
                item.points = new_points
                item.save()
        self.stdout.write('{} definitions, {} points changed'.format(total, changed))

        total = 0
        changed = 0
        for item in queryset_generator(get_user_model().objects.all()):
            total += 1
            new_points = 100 if not item.is_admin else 0
            if new_points != item.points:
                changed += 1
                item.points = new_points
                item.save()
        self.stdout.write('{} users, {} points changed'.format(total, changed))
