import requests
from django.shortcuts import render

test_body = r"""The [harmonic number](=harmonic-number) $H_n$ is defined as

$$
H_n = 1 + \frac{1}{2} + \ldots + \frac{1}{n} = \sum_{k=1}^n \frac{1}{k}
$$

for $n \geq 1$."""

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
        body = request.POST['src']
        data = node_request('/preview-item', {'text': body})
        context['item_html'] = data['html']
        context['body'] = body
    else:
        context['body'] = test_body
    return render(request, 'main/test-item-prep.html', context)
