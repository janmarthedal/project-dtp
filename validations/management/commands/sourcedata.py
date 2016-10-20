import json
import requests
from django.core.management.base import BaseCommand, CommandError
from validations.models import Source

class Command(BaseCommand):
    help = 'Fetch metadata for sources'

    def add_arguments(self, parser):
        parser.add_argument('--refresh', dest='refresh', default=False, action='store_true',
                            help='Attempt to refresh all, regardless of existing data')

    def handle(self, *args, **options):
        prev_id = 0
        try:
            while True:
                query = Source.objects.filter(id__gt=prev_id)
                if not options['refresh']:
                    query = query.filter(metadata='')
                source = query.order_by('id')[0]
                self.stdout.write('Checking {}'.format(source))
                if source.source_type in ['isbn10', 'isbn13']:
                    self.stdout.write('Trying to fetch isbn info from google books api')
                    r = requests.get('https://www.googleapis.com/books/v1/volumes?q=isbn:' + source.source_value)
                    data = r.json()
                    if data.get('totalItems', 0) > 0:
                        data = data['items'][0]['volumeInfo']
                        metadata = {key: data[key]
                                    for key in ['title', 'authors', 'publisher', 'publishedDate']
                                    if key in data}
                        source.metadata = json.dumps(metadata)
                        source.save()
                prev_id = source.id
        except IndexError:
            pass
        self.stdout.write(self.style.SUCCESS('Done'))
