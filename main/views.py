from django.shortcuts import render
from django.views.decorators.http import require_safe
from items.models import DraftItem, FinalItem

@require_safe
def index(request):
    c = {
        'finalitems':  list(FinalItem.objects.filter(status='F').order_by('-created_at')),
        'reviewitems': list(DraftItem.objects.filter(status='R').order_by('-modified_at')),
        }
    return render(request, 'index.html', c)

