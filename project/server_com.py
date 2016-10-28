import requests
from django.conf import settings

SERVER_HOST = 'http://localhost:3000' if settings.DEBUG else 'http://nodejs:3000'

def node_request(path, payload):
    r = requests.post(SERVER_HOST + path, json=payload)
    r.raise_for_status()
    return r.json()

def prepare_item(body):
    result = node_request('/prepare-item', {
        'body': body,
    })
    return result['document'], result['eqns']

def prep_item(body):
    result = node_request('/prep-item', {
        'body': body,
    })
    return result['document'], result['eqns']

def render_eqns(eqns):
    result = node_request('/render-eqns', {
        'eqns': eqns,
    })
    return result


"""
IN: item_type, document, eqns, refs
OUT: {html, errors, defines}
"""
def render_item(item_type, document, eqns, refs):
    return node_request('/render-item', {
        'item_type': item_type,
        'document': document,
        'eqns': eqns,
        'refs': refs,
    })
