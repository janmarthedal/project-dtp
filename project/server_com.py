import requests
from django.conf import settings

SERVER_HOST = 'http://localhost:3000' if settings.DEBUG else 'http://nodejs:3000'


def node_request(path, payload):
    r = requests.post(SERVER_HOST + path, json=payload)
    r.raise_for_status()
    return r.json()


def convert_markup(body):
    result = node_request('/prepare-item', {'body': body})
    return result['document'], result['eqns'], result['concepts']


def render_eqns(eqns):
    return node_request('/render-eqns', {'eqns': eqns})


# IN: item_type, document, eqns, concepts, refs, media_refs
# OUT: {html, errors, defines}
def render_item(item_type, document, eqns, concepts, refs, media_refs):
    return node_request('/render-item', {
        'item_type': item_type,
        'document': document,
        'eqns': eqns,
        'concepts': concepts,
        'refs': refs,
        'media': media_refs
    })


def parse_cindy(filename):
    return node_request('/parse-cindy', {
        'html_file': filename
    })
