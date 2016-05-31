import requests

"""def capfirst(value):
    return value and value[0].upper() + value[1:]"""

def node_request(path, payload):
    r = requests.post('http://localhost:3000' + path, json=payload)
    r.raise_for_status()
    return r.json()
