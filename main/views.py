from django.shortcuts import render
from django.views.decorators.http import require_safe
from items.models import Item

@require_safe
def index(request):
    c = {
        'finalitems':  list(Item.objects.filter(status='F').order_by('-final_at')),
        'reviewitems': list(Item.objects.filter(status='R').order_by('-modified_at')),
        }
    return render(request, 'index.html', c)

