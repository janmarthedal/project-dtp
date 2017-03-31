ES_HOSTS = ['http://elastic:changeme@localhost:9200']
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
        'uses': [c.concept.name for c in item.conceptreference_set.all()],
        'keyword': [c.keyword.name for c in item.itemkeyword_set.all()],
        'text': collect_body_text(item.get_body_root())
    }
    if item.is_def():
        body['defines'] = [c.concept.name for c in item.conceptdefinition_set.all()]
    return {
        'id': item.get_name(),
        'body': body
    }
