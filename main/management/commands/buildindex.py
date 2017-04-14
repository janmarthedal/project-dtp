from django.core.management.base import BaseCommand

from main.elasticsearch import create_index, index_item, index_media, refresh_index
from mathitems.models import MathItem
from media.models import Media


class Command(BaseCommand):
    help = '(Re)build search index'

    def handle(self, *args, **options):
        if create_index():
            self.stdout.write('Created index (removing existing)')
        else:
            self.stdout.write('Created index')

        self.stdout.write('Indexing items')
        for item in MathItem.objects.all():
            self.stdout.write('  ' + item.get_name())
            index_item(item)

        self.stdout.write('Indexing media')
        for media in Media.objects.all():
            self.stdout.write('  ' + media.get_name())
            index_media(media)

        self.stdout.write('Refreshing index')
        refresh_index()

        self.stdout.write(self.style.SUCCESS('Done'))
