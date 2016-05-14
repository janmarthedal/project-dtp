from django.shortcuts import render

def test_eqn(request):
    return render(request, 'main/test-eqn.html')
