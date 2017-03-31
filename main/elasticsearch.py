from django.db.models import Q
from django.conf import settings
from elasticsearch import Elasticsearch

from concepts.models import Concept
from keywords.models import Keyword


if settings.DEBUG:
    ES_HOSTS = ['http://elastic:changeme@localhost:9200']
else:
    ES_HOSTS = ['http://elastic:changeme@elasticsearch:9200']
ES_INDEX = 'items'
ES_TYPE = 'item'
ES_INDEX_CONF = {
    "settings": {
        "refresh_interval": -1,
        "number_of_shards": 1,
        "number_of_replicas": 0
    },
    "mappings": {
        "item": {
            "properties": {
                "type": {
                    "type": "keyword"
                },
                "defines": {
                    "type": "keyword"
                },
                "uses": {
                    "type": "keyword"
                },
                "keyword": {
                    "type": "text"
                },
                "text": {
                    "type": "text"
                }
            }
        }
    }
}


def collect_body_text(node):
    result = [txt for child in node.get('children', []) for txt in collect_body_text(child)]
    if node['type'] == 'text':
        result.append(node['value'])
    return result


def item_to_es_document(item):
    body = {
        'type': item.get_item_type_display().lower(),
        'uses': [c.name for c in Concept.objects.exclude(name='*')
                    .filter(Q(itemdependency__item=item) | Q(conceptreference__item=item)).distinct()],
        'keyword': [kw.name for kw in Keyword.objects.filter(itemkeyword__item=item)],
        'text': collect_body_text(item.get_body_root())
    }
    if item.is_def():
        body['defines'] = [c.concept.name for c in item.conceptdefinition_set.all()]
    return {
        'id': item.get_name(),
        'body': body
    }


# import json
# import logging
# logger = logging.getLogger(__name__)
def item_search(query, type_name, offset, limit):
    es = Elasticsearch(ES_HOSTS)
    results = es.search(ES_INDEX, ES_TYPE, from_=offset, size=limit, _source=False, body={
        'query': {
            'bool': {
                'must': [
                    {
                        "match_phrase": {
                            "type": type_name
                        }
                    },
                    {
                        'multi_match': {
                            'query': query,
                            'type': 'cross_fields',
                            'fields': ["defines^8", "uses^4", "keyword^2", "text"]
                        }
                    }
                ]
            }
        }
    })
    # logger.info(json.dumps(results, indent=2))
    return [hit['_id'] for hit in results['hits']['hits']], results['hits']['total']
