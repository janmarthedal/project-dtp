import requests
from django.shortcuts import render

def test_eqn(request):
    context = {'title': 'Test Equation'}
    if request.method == 'POST':
        eqn = request.POST['eqn']
        payload = {'eqns': [{'id': 1, 'format': 'inline-TeX', 'math': eqn}]}
        r = requests.post('http://localhost:3000/typeset', json=payload)
        data = r.json()
        context['eqn'] = data[0]['html']
    return render(request, 'main/test-eqn.html', context)

def test_item_prep(request):
    context = {'title': 'Test Item Prep'}
    if request.method == 'POST':
        src = request.POST['src']
        payload = {'text': src}
        r = requests.post('http://localhost:3000/prep-md-item', json=payload)
        r.raise_for_status()
        data = r.json()
        context['doc'] = data['document']

        r = requests.post('http://localhost:3000/typeset', json={'eqns': data['eqns']})
        r.raise_for_status()
        data = r.json()
        context['eqns'] = data

    return render(request, 'main/test-item-prep.html', context)
