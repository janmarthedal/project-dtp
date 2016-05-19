import requests
from django.shortcuts import render

def node_request(path, payload):
    r = requests.post('http://localhost:3000' + path, json=payload)
    r.raise_for_status()
    return r.json()

def test_eqn(request):
    context = {'title': 'Test Equation'}
    if request.method == 'POST':
        data = node_request('/typeset-eqns', {
            'eqns': [{
                'id': 1,
                'format': 'inline-TeX',
                'math': request.POST['eqn']
            }]
        })
        context['eqn'] = data[0]['html']
    return render(request, 'main/test-eqn.html', context)

def test_item_prep(request):
    context = {'title': 'Test Item Prep'}
    if request.method == 'POST':
        data = node_request('/prep-md-item', {'text': request.POST['src']})
        item_dom = data['document']

        data = node_request('/typeset-eqns', {'eqns': data['eqns']})
        eqns = data

        data = node_request('/typeset-item', {'document': item_dom})
        context['item_html'] = data['html']

    return render(request, 'main/test-item-prep.html', context)
