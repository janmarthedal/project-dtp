import json
import requests
from django.core.management.base import BaseCommand, CommandError

from concepts.models import ConceptDefinition, ConceptReference, ItemDependency
from equations.models import ItemEquation
from main.item_helpers import create_item_meta_data
from mathitems.models import MathItem


class Command(BaseCommand):
    help = 'Recreate metadata for items'

    def handle(self, *args, **options):
        ConceptDefinition.objects.all().delete()
        ConceptReference.objects.all().delete()
        ItemDependency.objects.all().delete()
        ItemEquation.objects.all().delete()
        for item in MathItem.objects.all():
            self.stdout.write('{}\n'.format(item.get_name()))
            create_item_meta_data(item)
        self.stdout.write(self.style.SUCCESS('Done'))
