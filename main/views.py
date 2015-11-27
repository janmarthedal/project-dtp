from django.http import Http404
from django.shortcuts import render

def create(request, item_type):
    if item_type not in ['definition', 'theorem', 'proof']:
        raise Http404
    return render(request, 'main/create.html', {'itemtype': item_type})
