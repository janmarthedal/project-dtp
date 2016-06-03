import requests


def node_request(path, payload):
    r = requests.post('http://localhost:3000' + path, json=payload)
    r.raise_for_status()
    return r.json()


def prepare_item(body):
    result = node_request('/prepare-item', {
        'body': body,
    })
    return result['document'], result['eqns']


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
