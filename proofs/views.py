from django.shortcuts import render
from items.models import FinalItem

def index(request):
    c = {
        'finalitems':  list(FinalItem.objects.filter(itemtype='P', status='F').order_by('-created_at')[:5]),
        }
    return render(request, 'proofs/index.html', c) 
