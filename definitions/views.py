from django.shortcuts import render
from items.models import FinalItem

def index(request):
    c = {
        'finalitems':  list(FinalItem.objects.filter(itemtype='D', status='F').order_by('-created_at')[:5]),
        }
    return render(request, 'definitions/index.html', c) 
