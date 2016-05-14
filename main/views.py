from django.shortcuts import render

def test_eqn(request):
    context = {'title': 'Test Equation'}
    return render(request, 'main/test-eqn.html', context)
