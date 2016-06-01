import requests


def node_request(path, payload):
    r = requests.post('http://localhost:3000' + path, json=payload)
    r.raise_for_status()
    return r.json()


def prepare_item(body):
    return node_request('/prepare-item', {'text': body})


def render_item(item_data):
    return node_request('/render-item', item_data)
