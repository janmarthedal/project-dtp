from django.shortcuts import render
from items.models import FinalItem

def index(request):
    c = {
        'finalitems':  list(FinalItem.objects.filter(itemtype='T', status='F').order_by('-created_at')[:5]),
        }
    return render(request, 'theorems/index.html', c) 
