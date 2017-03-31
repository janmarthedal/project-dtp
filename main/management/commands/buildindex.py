from django.core.management.base import BaseCommand
from elasticsearch import Elasticsearch

from main.elasticsearch import ES_HOSTS, ES_INDEX, ES_TYPE, ES_INDEX_CONF, item_to_es_document
from mathitems.models import MathItem


class Command(BaseCommand):
    help = '(Re)build search index'

    def handle(self, *args, **options):
        es = Elasticsearch(ES_HOSTS)

        if es.indices.exists(ES_INDEX):
            self.stdout.write('Index already exists, removing')
            es.indices.delete(ES_INDEX)

        self.stdout.write('Creating index')
        es.indices.create(ES_INDEX, body=ES_INDEX_CONF)

        self.stdout.write('Indexing')
        for item in MathItem.objects.all():
            data = item_to_es_document(item)
            self.stdout.write('  ' + data['id'])
            es.index(ES_INDEX, ES_TYPE, id=data['id'], body=data['body'])

        self.stdout.write('Refreshing index')
        es.indices.refresh(ES_INDEX)

        self.stdout.write(self.style.SUCCESS('Done'))
