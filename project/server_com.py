import requests
from django.conf import settings

SERVER_HOST = 'http://localhost:3000' if settings.DEBUG else 'http://nodejs:3000'


def node_request(path, json):
    r = requests.post(SERVER_HOST + path, json=json)
    r.raise_for_status()
    return r.json()


def convert_markup(body):
    result = node_request('/prepare-item', json={'body': body})
    return result['document'], result['eqns'], result['concepts']


def render_eqns(eqns):
    return node_request('/render-eqns', json={'eqns': eqns})


# IN: item_type, document, eqns, concepts, refs, media_refs
# OUT: {html, errors, defines}
def render_item(item_type, document, eqns, concepts, refs, media_refs):
    return node_request('/render-item', json={
        'item_type': item_type,
        'document': document,
        'eqns': eqns,
        'concepts': concepts,
        'refs': refs,
        'media': media_refs
    })


def parse_json_relaxed(data):
    return node_request('/parse-json-relaxed', json={
        'data': data
    })


def parse_cindy(filename):
    return node_request('/parse-cindy', json={
        'html_file': filename
    })
