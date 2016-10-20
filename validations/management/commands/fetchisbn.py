import json
import requests
from django.core.management.base import BaseCommand, CommandError
from validations.models import Source

class Command(BaseCommand):
    help = 'Fetches metadata for sources of type isbn'

    #def add_arguments(self, parser):
    #    parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        prev_id = 0
        try:
            while True:
                source = Source.objects.filter(source_type__in=['isbn10', 'isbn13'],
                                               metadata='',
                                               id__gt=prev_id).order_by('id')[0]
                self.stdout.write('Fetching data for {}'.format(source))
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
