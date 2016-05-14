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
